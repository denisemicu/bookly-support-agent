from __future__ import annotations

import json
import os
import re
from typing import Any, Optional

from dotenv import load_dotenv
from openai import OpenAI

from tools import (
    cancel_order,
    check_return_eligibility,
    create_missing_package_claim,
    create_return_request,
    extract_order_ids,
    get_bookly_policy_answer,
    get_order_details,
    get_refund_status,
    normalize_order_id,
    update_shipping_address,
)

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = (
    OpenAI(
        api_key=OPENAI_API_KEY,
        timeout=12.0,
        max_retries=0,
    )
    if OPENAI_API_KEY
    else None
)

VALID_INTENTS = {
    "order_status",
    "return_request",
    "return_eligibility",
    "refund_status",
    "cancel_order",
    "change_address",
    "missing_package",
    "shipping_policy",
    "return_policy",
    "refund_policy",
    "cancellation_policy",
    "address_policy",
    "password_reset",
    "other",
}

ACTION_CONFIRMATIONS = {
    "create_return_request",
    "cancel_order",
    "update_shipping_address",
    "create_missing_package_claim",
}


def make_state(
    *,
    active_order_id: str | None = None,
    pending_action: str | None = None,
    pending_intent: str | None = None,
    return_reason: str | None = None,
    new_address: str | None = None,
    awaiting: str | None = None,
) -> dict[str, Any]:
    return {
        "active_order_id": active_order_id,
        "pending_action": pending_action,
        "pending_intent": pending_intent,
        "return_reason": return_reason,
        "new_address": new_address,
        "awaiting": awaiting,
    }


def response(
    text: str,
    *,
    intent: str,
    action: str,
    tool_called: str | None = None,
    state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "response": text,
        "intent": intent,
        "action": action,
        "tool_called": tool_called,
        "state": state or make_state(),
    }


def normalize_text(text: str) -> str:
    return " ".join(text.lower().strip().split())


def get_last_message(
    history: list[dict[str, str]],
    role: str,
) -> Optional[str]:
    for message in reversed(history):
        if message.get("role") == role:
            return message.get("content", "")
    return None


def get_recent_user_messages(history: list[dict[str, str]]) -> list[str]:
    return [
        message.get("content", "")
        for message in history[-12:]
        if message.get("role") == "user"
    ]


def get_order_ids_from_history(history: list[dict[str, str]]) -> list[str]:
    order_ids: list[str] = []

    for message in history:
        if message.get("role") != "user":
            continue

        for order_id in extract_order_ids(message.get("content", "")):
            if order_id not in order_ids:
                order_ids.append(order_id)

    return order_ids


def get_most_recent_order_id(history: list[dict[str, str]]) -> str | None:
    for message in reversed(history):
        if message.get("role") != "user":
            continue

        order_ids = extract_order_ids(message.get("content", ""))

        if order_ids:
            return order_ids[-1]

    return None


def looks_like_incomplete_order_id(text: str) -> bool:
    compact = re.sub(r"[^a-zA-Z0-9]", "", text).upper()

    return (
        compact.startswith("BK")
        and compact != "BK"
        and not re.fullmatch(r"BK\d{4}", compact)
    )


def is_yes(text: str) -> bool:
    normalized = normalize_text(text)

    yes_values = {
        "yes",
        "y",
        "yeah",
        "yep",
        "sure",
        "please",
        "go ahead",
        "do it",
        "confirm",
        "confirmed",
        "okay",
        "ok",
    }

    return normalized in yes_values or normalized.startswith("yes ")


def is_no(text: str) -> bool:
    normalized = normalize_text(text)

    no_values = {
        "no",
        "n",
        "nope",
        "cancel",
        "never mind",
        "nevermind",
        "don't",
        "do not",
        "stop",
    }

    return normalized in no_values or normalized.startswith("no ")


def looks_like_order_status_request(text: str) -> bool:
    phrases = [
        "where is my order",
        "where's my order",
        "track my order",
        "track order",
        "tracking",
        "my book still hasn't arrived",
        "my book has not arrived",
        "my order hasn't arrived",
        "my order has not arrived",
        "when will it arrive",
        "when will my order arrive",
        "still waiting for my order",
        "delivery update",
        "where is it",
        "what is the status",
        "order status",
    ]

    normalized = normalize_text(text)

    return any(phrase in normalized for phrase in phrases)


def looks_like_return_request(text: str) -> bool:
    phrases = [
        "return",
        "send it back",
        "refund this book",
        "want my money back",
        "i don't want it",
        "i dont want it",
        "wrong format",
        "wrong edition",
        "wrong version",
        "wrong item",
        "wrong book",
        "hardcover",
        "paperback",
        "damaged",
        "defective",
        "duplicate",
        "accidentally bought",
        "bought by mistake",
        "ordered by mistake",
        "changed my mind",
        "not what i expected",
        "not what i wanted",
        "already own",
        "gift return",
    ]

    normalized = normalize_text(text)

    return any(phrase in normalized for phrase in phrases)


def looks_like_return_eligibility_request(text: str) -> bool:
    phrases = [
        "can i return",
        "return eligible",
        "eligible for a return",
        "can this be returned",
        "am i able to return",
    ]

    normalized = normalize_text(text)

    return any(phrase in normalized for phrase in phrases)


def looks_like_refund_request(text: str) -> bool:
    phrases = [
        "where is my refund",
        "refund status",
        "when will my refund",
        "did my refund",
        "refund pending",
        "refund completed",
    ]

    normalized = normalize_text(text)

    return any(phrase in normalized for phrase in phrases)


def looks_like_cancel_request(text: str) -> bool:
    phrases = [
        "cancel my order",
        "cancel order",
        "stop my order",
        "don't send it",
        "dont send it",
        "cancel the book",
    ]

    normalized = normalize_text(text)

    return any(phrase in normalized for phrase in phrases)


def looks_like_address_change_request(text: str) -> bool:
    phrases = [
        "change my address",
        "change shipping address",
        "update my address",
        "wrong address",
        "send it to a different address",
        "change where it is delivered",
    ]

    normalized = normalize_text(text)

    return any(phrase in normalized for phrase in phrases)


def looks_like_missing_package_request(text: str) -> bool:
    phrases = [
        "says delivered but",
        "marked delivered but",
        "never received",
        "didn't receive",
        "did not receive",
        "missing package",
        "package is missing",
        "stolen package",
        "not at my door",
    ]

    normalized = normalize_text(text)

    return any(phrase in normalized for phrase in phrases)


def looks_like_shipping_policy_request(text: str) -> bool:
    phrases = [
        "how long does delivery take",
        "how long does shipping take",
        "shipping policy",
        "shipping options",
        "expedited shipping",
        "standard shipping",
    ]

    normalized = normalize_text(text)

    return any(phrase in normalized for phrase in phrases)


def looks_like_return_policy_request(text: str) -> bool:
    phrases = [
        "return policy",
        "how long do i have to return",
        "return window",
        "returns policy",
    ]

    normalized = normalize_text(text)

    return any(phrase in normalized for phrase in phrases)


def looks_like_password_reset_request(text: str) -> bool:
    phrases = [
        "forgot my password",
        "reset my password",
        "can't log in",
        "cannot log in",
        "password reset",
    ]

    normalized = normalize_text(text)

    return any(phrase in normalized for phrase in phrases)


def infer_return_reason(text: str) -> str | None:
    normalized = normalize_text(text)

    reason_map = {
        "damaged": "Item arrived damaged",
        "defective": "Item arrived damaged",
        "wrong item": "Wrong item received",
        "wrong book": "Wrong item received",
        "wrong edition": "Wrong format ordered",
        "wrong format": "Wrong format ordered",
        "wrong version": "Wrong format ordered",
        "hardcover": "Wrong format ordered",
        "paperback": "Wrong format ordered",
        "duplicate": "Duplicate purchase",
        "already own": "Duplicate purchase",
        "accidentally bought": "Accidental purchase",
        "bought by mistake": "Accidental purchase",
        "ordered by mistake": "Accidental purchase",
        "changed my mind": "Changed my mind",
        "gift": "Gift return",
        "arrived late": "Arrived too late",
        "too late": "Arrived too late",
    }

    for phrase, reason in reason_map.items():
        if phrase in normalized:
            return reason

    return None


def find_return_reason_in_history(history: list[dict[str, str]]) -> str | None:
    for message in reversed(history):
        if message.get("role") != "user":
            continue

        reason = infer_return_reason(message.get("content", ""))

        if reason:
            return reason

    return None


def looks_like_address(text: str) -> bool:
    normalized = " ".join(text.strip().split())

    has_number = bool(re.search(r"\b\d{1,6}\b", normalized))
    has_street_word = bool(
        re.search(
            r"\b(street|st|avenue|ave|road|rd|lane|ln|drive|dr|boulevard|blvd|way|court|ct|place|pl)\b",
            normalized,
            flags=re.IGNORECASE,
        )
    )

    return has_number and has_street_word and len(normalized) >= 10


def find_address_in_history(history: list[dict[str, str]]) -> str | None:
    for message in reversed(history):
        if message.get("role") != "user":
            continue

        content = message.get("content", "")

        if looks_like_address(content):
            return content.strip()

    return None


def classify_customer_message(
    user_message: str,
    history: list[dict[str, str]],
) -> dict[str, Any]:
    if not client:
        return {
            "intent": "other",
            "confidence": 0.0,
            "reason": "OpenAI API key is not configured.",
        }

    recent_history = history[-8:]

    system_prompt = """
You are an intent classifier for Bookly, an online bookstore.

Classify the customer's latest message into exactly one intent:
- order_status
- return_request
- return_eligibility
- refund_status
- cancel_order
- change_address
- missing_package
- shipping_policy
- return_policy
- refund_policy
- cancellation_policy
- address_policy
- password_reset
- other

Return ONLY valid JSON with this exact shape:
{
  "intent": "one of the allowed intent values",
  "confidence": 0.0,
  "reason": "brief explanation"
}

Rules:
- Do not answer the customer.
- Do not invent order details.
- Do not choose an order ID.
- Do not decide whether an action should be taken.
- Use conversation context only to understand follow-up messages.
"""

    conversation_context = "\n".join(
        f"{message.get('role', 'unknown')}: {message.get('content', '')}"
        for message in recent_history
    )

    user_prompt = f"""
Conversation so far:
{conversation_context or "(no prior conversation)"}

Latest customer message:
{user_message}
"""

    try:
        completion = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        content = completion.choices[0].message.content or "{}"
        result = json.loads(content)

        if result.get("intent") not in VALID_INTENTS:
            raise ValueError(f"Unsupported intent: {result.get('intent')}")

        return result

    except Exception as error:
        print(
            f"LLM classification failed: {type(error).__name__}: {error}",
            flush=True,
        )

        return {
            "intent": "other",
            "confidence": 0.0,
            "reason": "LLM classification unavailable.",
        }


def deterministic_intent(text: str) -> str | None:
    if looks_like_missing_package_request(text):
        return "missing_package"

    if looks_like_address_change_request(text):
        return "change_address"

    if looks_like_cancel_request(text):
        return "cancel_order"

    if looks_like_refund_request(text):
        return "refund_status"

    if looks_like_return_eligibility_request(text):
        return "return_eligibility"

    if looks_like_return_request(text):
        return "return_request"

    if looks_like_order_status_request(text):
        return "order_status"

    if looks_like_shipping_policy_request(text):
        return "shipping_policy"

    if looks_like_return_policy_request(text):
        return "return_policy"

    if looks_like_password_reset_request(text):
        return "password_reset"

    return None


def ask_for_order_id(
    *,
    intent: str,
    state: dict[str, Any],
    prefix: str | None = None,
) -> dict[str, Any]:
    message = prefix or "I can help with that."

    return response(
        f"{message} What is your Bookly order ID? It should look like BK-1234.",
        intent=intent,
        action="clarifying_question",
        state={
            **state,
            "pending_intent": intent,
            "awaiting": "order_id",
        },
    )


def ask_to_choose_order(
    *,
    order_ids: list[str],
    intent: str,
    state: dict[str, Any],
) -> dict[str, Any]:
    readable_ids = " and ".join(order_ids)

    return response(
        f"I found multiple Bookly orders in this conversation: {readable_ids}. Which order would you like help with?",
        intent=intent,
        action="disambiguate_order",
        state={
            **state,
            "awaiting": "order_selection",
        },
    )


def format_order_status(order: dict[str, Any]) -> str:
    status = order["status"]
    book = f"{order['book_title']} ({order['format']})"

    if status == "processing":
        return (
            f"Order {order['order_id']} for {book} is still processing. "
            f"It is expected to ship soon, with an estimated arrival of {order['eta']}."
        )

    if status == "shipped":
        delay_note = (
            " It is currently delayed in transit."
            if order["shipment_status"] == "delayed"
            else ""
        )

        return (
            f"Order {order['order_id']} for {book} has shipped with "
            f"{order['carrier']}. Tracking number: {order['tracking_number']}. "
            f"Estimated arrival: {order['eta']}.{delay_note}"
        )

    if status == "delivered":
        return (
            f"Order {order['order_id']} for {book} was delivered on "
            f"{order['delivered_at']}."
        )

    return (
        f"Order {order['order_id']} for {book} was canceled. "
        "A refund is pending to the original payment method."
    )


def execute_pending_action(
    *,
    pending_action: str,
    order_id: str,
    return_reason: str | None,
    new_address: str | None,
) -> dict[str, Any]:
    if pending_action == "create_return_request":
        return create_return_request(
            order_id,
            return_reason or "Other",
        )

    if pending_action == "cancel_order":
        return cancel_order(order_id)

    if pending_action == "update_shipping_address":
        return update_shipping_address(
            order_id,
            new_address or "",
        )

    if pending_action == "create_missing_package_claim":
        return create_missing_package_claim(order_id)

    return {
        "success": False,
        "message": "I was unable to complete that request. Please try again.",
    }


def handle_confirmation(
    *,
    user_message: str,
    state: dict[str, Any],
) -> dict[str, Any] | None:
    pending_action = state.get("pending_action")

    if pending_action not in ACTION_CONFIRMATIONS:
        return None

    order_id = state.get("active_order_id")

    if not order_id:
        return response(
            "I lost the order reference for that request. What is your Bookly order ID?",
            intent=state.get("pending_intent") or "other",
            action="clarifying_question",
            state=make_state(
                pending_intent=state.get("pending_intent"),
                awaiting="order_id",
            ),
        )

    if is_no(user_message):
        return response(
            "No problem — I have not made any changes to your order.",
            intent=state.get("pending_intent") or "other",
            action="action_cancelled_by_customer",
            state=make_state(active_order_id=order_id),
        )

    if not is_yes(user_message):
        return response(
            "Please reply yes to confirm, or no to cancel this request.",
            intent=state.get("pending_intent") or "other",
            action="awaiting_confirmation",
            state=state,
        )

    result = execute_pending_action(
        pending_action=pending_action,
        order_id=order_id,
        return_reason=state.get("return_reason"),
        new_address=state.get("new_address"),
    )

    return response(
        result["message"],
        intent=state.get("pending_intent") or "other",
        action=pending_action,
        tool_called=pending_action,
        state=make_state(active_order_id=order_id),
    )


def handle_order_status(order_id: str) -> dict[str, Any]:
    result = get_order_details(order_id)

    if not result["found"]:
        return response(
            result["message"],
            intent="order_status",
            action="invalid_order_id",
            tool_called="get_order_details",
            state=make_state(awaiting="order_id"),
        )

    order = result["order"]

    return response(
        format_order_status(order),
        intent="order_status",
        action="order_status_response",
        tool_called="get_order_details",
        state=make_state(active_order_id=order["order_id"]),
    )


def handle_return_eligibility(order_id: str) -> dict[str, Any]:
    result = check_return_eligibility(order_id)

    if not result.get("found"):
        return response(
            result["message"],
            intent="return_eligibility",
            action="invalid_order_id",
            tool_called="check_return_eligibility",
            state=make_state(awaiting="order_id"),
        )

    return response(
        result["message"],
        intent="return_eligibility",
        action="return_eligibility_response",
        tool_called="check_return_eligibility",
        state=make_state(active_order_id=result["order"]["order_id"]),
    )


def handle_return_request(
    *,
    order_id: str,
    return_reason: str | None,
) -> dict[str, Any]:
    eligibility = check_return_eligibility(order_id)

    if not eligibility.get("found"):
        return response(
            eligibility["message"],
            intent="return_request",
            action="invalid_order_id",
            tool_called="check_return_eligibility",
            state=make_state(awaiting="order_id"),
        )

    if not eligibility.get("eligible"):
        return response(
            eligibility["message"],
            intent="return_request",
            action="return_not_eligible",
            tool_called="check_return_eligibility",
            state=make_state(active_order_id=order_id),
        )

    if not return_reason:
        return response(
            "I found the order and it is eligible for a return. What is the reason for the return?",
            intent="return_request",
            action="clarifying_question",
            tool_called="check_return_eligibility",
            state=make_state(
                active_order_id=order_id,
                pending_intent="return_request",
                awaiting="return_reason",
            ),
        )

    order = eligibility["order"]

    return response(
        (
            f"I can create a return for {order['book_title']} "
            f"({order['format']}) from order {order_id}. "
            f"Reason: {return_reason}. Would you like me to go ahead?"
        ),
        intent="return_request",
        action="awaiting_confirmation",
        tool_called="check_return_eligibility",
        state=make_state(
            active_order_id=order_id,
            pending_action="create_return_request",
            pending_intent="return_request",
            return_reason=return_reason,
            awaiting="confirmation",
        ),
    )


def handle_cancel_order(order_id: str) -> dict[str, Any]:
    result = get_order_details(order_id)

    if not result["found"]:
        return response(
            result["message"],
            intent="cancel_order",
            action="invalid_order_id",
            tool_called="get_order_details",
            state=make_state(awaiting="order_id"),
        )

    order = result["order"]

    if not order["cancellation_eligible"]:
        failed_result = cancel_order(order_id)

        return response(
            failed_result["message"],
            intent="cancel_order",
            action="cancellation_not_available",
            tool_called="cancel_order",
            state=make_state(active_order_id=order_id),
        )

    return response(
        (
            f"Order {order_id} is still processing and can be canceled. "
            "Would you like me to cancel it?"
        ),
        intent="cancel_order",
        action="awaiting_confirmation",
        tool_called="get_order_details",
        state=make_state(
            active_order_id=order_id,
            pending_action="cancel_order",
            pending_intent="cancel_order",
            awaiting="confirmation",
        ),
    )


def handle_address_change(
    *,
    order_id: str,
    new_address: str | None,
) -> dict[str, Any]:
    result = get_order_details(order_id)

    if not result["found"]:
        return response(
            result["message"],
            intent="change_address",
            action="invalid_order_id",
            tool_called="get_order_details",
            state=make_state(awaiting="order_id"),
        )

    order = result["order"]

    if not order["address_change_eligible"]:
        failed_result = update_shipping_address(order_id, new_address or "")

        return response(
            failed_result["message"],
            intent="change_address",
            action="address_change_not_available",
            tool_called="update_shipping_address",
            state=make_state(active_order_id=order_id),
        )

    if not new_address:
        return response(
            "I can update the address for that order. Please send the full new shipping address, including city, state, and ZIP code.",
            intent="change_address",
            action="clarifying_question",
            tool_called="get_order_details",
            state=make_state(
                active_order_id=order_id,
                pending_intent="change_address",
                awaiting="new_address",
            ),
        )

    return response(
        (
            f"I can update the shipping address for order {order_id} to: "
            f"{new_address}. Would you like me to make that change?"
        ),
        intent="change_address",
        action="awaiting_confirmation",
        tool_called="get_order_details",
        state=make_state(
            active_order_id=order_id,
            pending_action="update_shipping_address",
            pending_intent="change_address",
            new_address=new_address,
            awaiting="confirmation",
        ),
    )


def handle_missing_package(order_id: str) -> dict[str, Any]:
    result = get_order_details(order_id)

    if not result["found"]:
        return response(
            result["message"],
            intent="missing_package",
            action="invalid_order_id",
            tool_called="get_order_details",
            state=make_state(awaiting="order_id"),
        )

    order = result["order"]

    if order["status"] != "delivered":
        return response(
            (
                f"Order {order_id} is not marked as delivered yet. "
                "I can check the tracking status instead."
            ),
            intent="missing_package",
            action="missing_package_not_applicable",
            tool_called="get_order_details",
            state=make_state(active_order_id=order_id),
        )

    return response(
        (
            f"Order {order_id} is marked as delivered. I can start a "
            "missing-package claim with Bookly support. Would you like me to proceed?"
        ),
        intent="missing_package",
        action="awaiting_confirmation",
        tool_called="get_order_details",
        state=make_state(
            active_order_id=order_id,
            pending_action="create_missing_package_claim",
            pending_intent="missing_package",
            awaiting="confirmation",
        ),
    )


def handle_refund_status(order_id: str) -> dict[str, Any]:
    result = get_refund_status(order_id)

    if not result.get("found"):
        return response(
            result["message"],
            intent="refund_status",
            action="invalid_order_id",
            tool_called="get_refund_status",
            state=make_state(awaiting="order_id"),
        )

    return response(
        result["message"],
        intent="refund_status",
        action="refund_status_response",
        tool_called="get_refund_status",
        state=make_state(active_order_id=order_id),
    )


def resolve_intent(
    *,
    user_message: str,
    history: list[dict[str, str]],
) -> str:
    local_intent = deterministic_intent(user_message)

    if local_intent:
        return local_intent

    classification = classify_customer_message(user_message, history)

    return classification.get("intent", "other")


def run_bookly_agent(
    user_message: str,
    history: list[dict[str, str]] | None = None,
    state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    history = history or []
    state = state or make_state()

    user_message = user_message.strip()

    if not user_message:
        return response(
            "What can I help you with today?",
            intent="other",
            action="empty_message",
            state=state,
        )

    confirmation_result = handle_confirmation(
        user_message=user_message,
        state=state,
    )

    if confirmation_result:
        return confirmation_result

    current_order_ids = extract_order_ids(user_message)
    historical_order_ids = get_order_ids_from_history(history)

    if len(current_order_ids) > 1:
        return ask_to_choose_order(
            order_ids=current_order_ids,
            intent=state.get("pending_intent") or "other",
            state=state,
        )

    if looks_like_incomplete_order_id(user_message) and not current_order_ids:
        return response(
            "That looks like an incomplete Bookly order ID. Please send the full ID in the format BK-1234.",
            intent=state.get("pending_intent") or "other",
            action="invalid_order_id",
            state={
                **state,
                "awaiting": "order_id",
            },
        )

    order_id = (
        current_order_ids[0]
        if current_order_ids
        else state.get("active_order_id")
        or get_most_recent_order_id(history)
    )

    pending_intent = state.get("pending_intent")
    awaiting = state.get("awaiting")

    if awaiting == "order_selection" and current_order_ids:
        order_id = current_order_ids[0]

    if awaiting == "order_id":
        if not order_id:
            return ask_for_order_id(
                intent=pending_intent or "other",
                state=state,
            )

        if pending_intent == "order_status":
            return handle_order_status(order_id)

        if pending_intent == "return_request":
            return handle_return_request(
                order_id=order_id,
                return_reason=state.get("return_reason")
                or find_return_reason_in_history(history),
            )

        if pending_intent == "return_eligibility":
            return handle_return_eligibility(order_id)

        if pending_intent == "refund_status":
            return handle_refund_status(order_id)

        if pending_intent == "cancel_order":
            return handle_cancel_order(order_id)

        if pending_intent == "change_address":
            return handle_address_change(
                order_id=order_id,
                new_address=state.get("new_address"),
            )

        if pending_intent == "missing_package":
            return handle_missing_package(order_id)

    if awaiting == "return_reason":
        reason = infer_return_reason(user_message) or user_message

        if not order_id:
            return ask_for_order_id(
                intent="return_request",
                state=make_state(
                    pending_intent="return_request",
                    return_reason=reason,
                ),
            )

        return handle_return_request(
            order_id=order_id,
            return_reason=reason,
        )

    if awaiting == "new_address":
        if not looks_like_address(user_message):
            return response(
                "Please send the full new shipping address, including street address, city, state, and ZIP code.",
                intent="change_address",
                action="clarifying_question",
                state=state,
            )

        if not order_id:
            return ask_for_order_id(
                intent="change_address",
                state=make_state(
                    pending_intent="change_address",
                    new_address=user_message,
                ),
            )

        return handle_address_change(
            order_id=order_id,
            new_address=user_message,
        )

    intent = resolve_intent(
        user_message=user_message,
        history=history,
    )

    if intent in {
        "order_status",
        "return_request",
        "return_eligibility",
        "refund_status",
        "cancel_order",
        "change_address",
        "missing_package",
    }:
        if not order_id and len(historical_order_ids) > 1:
            return ask_to_choose_order(
                order_ids=historical_order_ids[-2:],
                intent=intent,
                state=make_state(pending_intent=intent),
            )

        if not order_id:
            prefix_map = {
                "order_status": "I can check that for you.",
                "return_request": "I can help start a return.",
                "return_eligibility": "I can check whether your order is eligible for a return.",
                "refund_status": "I can check the refund status.",
                "cancel_order": "I can check whether that order can still be canceled.",
                "change_address": "I can check whether the shipping address can still be updated.",
                "missing_package": "I’m sorry that happened. I can help with a missing-package claim.",
            }

            return ask_for_order_id(
                intent=intent,
                state=make_state(pending_intent=intent),
                prefix=prefix_map[intent],
            )

    if intent == "order_status":
        return handle_order_status(order_id)

    if intent == "return_eligibility":
        return handle_return_eligibility(order_id)

    if intent == "return_request":
        return handle_return_request(
            order_id=order_id,
            return_reason=infer_return_reason(user_message)
            or find_return_reason_in_history(history),
        )

    if intent == "refund_status":
        return handle_refund_status(order_id)

    if intent == "cancel_order":
        return handle_cancel_order(order_id)

    if intent == "change_address":
        return handle_address_change(
            order_id=order_id,
            new_address=find_address_in_history(history)
            if looks_like_address(user_message)
            else None,
        )

    if intent == "missing_package":
        return handle_missing_package(order_id)

    policy_map = {
        "shipping_policy": "shipping",
        "return_policy": "returns",
        "refund_policy": "refunds",
        "cancellation_policy": "cancellations",
        "address_policy": "address_changes",
        "password_reset": "password_reset",
    }

    if intent in policy_map:
        return response(
            get_bookly_policy_answer(policy_map[intent]),
            intent=intent,
            action="policy_lookup",
            tool_called="get_bookly_policy_answer",
            state=make_state(active_order_id=order_id),
        )

    return response(
        (
            "I can help with order tracking, returns, refunds, cancellations, "
            "shipping-address changes, missing packages, shipping questions, "
            "and password resets. What would you like help with?"
        ),
        intent="other",
        action="fallback",
        state=make_state(active_order_id=order_id),
    )