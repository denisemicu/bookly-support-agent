import json
import os
import re
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

from tools import create_return_request, get_order_status

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=12.0,
    max_retries=0,
)


def extract_order_id(text: str) -> Optional[str]:
    """Find Bookly order IDs such as BK-1001."""
    match = re.search(r"BK-\d{4}", text, re.IGNORECASE)

    if match:
        return match.group(0).upper()

    return None


def get_last_assistant_message(history: list[dict]) -> Optional[str]:
    """Return the most recent assistant message."""
    for message in reversed(history):
        if message["role"] == "assistant":
            return message["content"]

    return None


def get_order_id_from_history(history: list[dict]) -> Optional[str]:
    """Find the most recent Bookly order ID in conversation history."""
    for message in reversed(history):
        order_id = extract_order_id(message["content"])

        if order_id:
            return order_id

    return None


def is_waiting_for_order_id(history: list[dict]) -> bool:
    """Check whether Pip most recently asked the customer for an order ID."""
    last_message = get_last_assistant_message(history)

    if not last_message:
        return False

    text = last_message.lower()

    return (
        "share your bookly order id" in text
        or "what is your bookly order id" in text
        or "share your order id" in text
        or "what is your order id" in text
    )


def is_waiting_for_return_reason(history: list[dict]) -> bool:
    """Check whether Pip most recently asked for a return reason."""
    last_message = get_last_assistant_message(history)

    if not last_message:
        return False

    return "reason for the return" in last_message.lower()


def looks_like_order_status_request(text: str) -> bool:
    """Catch common order-status language deterministically."""
    text = text.lower()

    phrases = [
        "where is my order",
        "where's my order",
        "track my order",
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
    ]

    return any(phrase in text for phrase in phrases)


def has_return_reason(text: str) -> bool:
    """
    Decide whether a message contains an actual return reason,
    rather than only saying the customer wants a return.
    """
    text = text.lower()

    reason_phrases = [
        "wrong edition",
        "wrong version",
        "wrong book",
        "wrong item",
        "wrong format",
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
        "gift",
        "arrived late",
        "too late",
        "missing pages",
        "already own",
    ]

    return any(phrase in text for phrase in reason_phrases)


def get_return_reason_from_history(history: list[dict]) -> Optional[str]:
    """
    Look backward through prior customer messages for a return reason.

    This is what lets Pip remember:
    'I accidentally bought the hardcover version'
    after it later asks for the order ID.
    """
    for message in reversed(history):
        if message["role"] == "user" and has_return_reason(message["content"]):
            return message["content"]

    return None


def format_order_status(order: dict) -> str:
    """Turn structured tool output into a customer-friendly response."""
    response = f"Order {order['order_id']} is currently {order['status']}."

    if order.get("carrier"):
        response += f" It shipped with {order['carrier']}."

    if order.get("tracking_number"):
        response += f" Tracking number: {order['tracking_number']}."

    if order.get("eta"):
        response += f" Estimated arrival: {order['eta']}."

    return response


def get_bookly_policy_answer(policy_topic: str) -> str:
    """
    Mock grounded policy knowledge base.
    In production, this could call a CMS, help center, or RAG system.
    """
    topic = policy_topic.lower()

    if topic == "shipping":
        return (
            "Bookly offers standard shipping in 3–5 business days and "
            "expedited shipping in 1–2 business days."
        )

    if topic == "returns":
        return (
            "Bookly accepts returns within 30 days of delivery for books in "
            "resellable condition."
        )

    if topic == "refunds":
        return (
            "Refunds are sent to the original payment method within 5–7 "
            "business days after Bookly receives the returned item."
        )

    if topic == "password_reset":
        return (
            "You can reset your password from the Bookly login page by "
            "selecting “Forgot password.”"
        )

    return (
        "I can help with order tracking, returns, refunds, shipping, and "
        "password resets."
    )


def classify_customer_message(user_message: str, history: list[dict]) -> dict:
    """
    Use the LLM only for constrained intent classification.

    The model does not execute tools, invent order details, or make
    customer-account decisions. Python orchestration remains in control.
    """
    recent_history = history[-6:]

    system_prompt = """
You are an intent classifier for Bookly, an online bookstore.

Classify the customer's latest message into exactly one intent:
- order_status
- return_request
- shipping_policy
- return_policy
- refund_policy
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
- Do not decide whether an action should be taken.
- Use conversation context for follow-up messages.
"""

    conversation_context = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in recent_history
    )

    user_prompt = f"""
Conversation so far:
{conversation_context or "(no prior conversation)"}

Latest customer message:
{user_message}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        content = response.choices[0].message.content or "{}"
        result = json.loads(content)

        allowed_intents = {
            "order_status",
            "return_request",
            "shipping_policy",
            "return_policy",
            "refund_policy",
            "password_reset",
            "other",
        }

        if result.get("intent") not in allowed_intents:
            raise ValueError(
                f"Unsupported intent returned: {result.get('intent')}"
            )

        return result

    except Exception as error:
        print(
            f"\nLLM classification failed: {type(error).__name__}: {error}\n"
        )

        return {
            "intent": "other",
            "confidence": 0.0,
            "reason": "LLM classification unavailable.",
        }


def run_order_status_flow(order_id: Optional[str]):
    """Handle the order-status workflow."""
    if not order_id:
        return {
            "response": (
                "I can help check your order status. "
                "Could you share your Bookly order ID? "
                "It should look like BK-1001."
            ),
            "action": "clarifying_question",
            "tool_called": None,
            "intent": "order_status",
        }

    result = get_order_status(order_id)

    if not result["found"]:
        return {
            "response": (
                "I couldn't find that order ID. "
                "Could you double-check it and send it again?"
            ),
            "action": "order_not_found",
            "tool_called": "get_order_status",
            "intent": "order_status",
        }

    return {
        "response": format_order_status(result["order"]),
        "action": "order_status_response",
        "tool_called": "get_order_status",
        "intent": "order_status",
    }


def run_return_flow(
    user_message: str,
    history: list[dict],
    current_order_id: Optional[str],
):
    """
    Handle the return workflow.

    Required fields:
    - order ID
    - return reason

    The agent can collect them in either order and reuse prior context.
    """
    order_id = current_order_id or get_order_id_from_history(history)

    current_message_is_reason = has_return_reason(user_message)
    prior_reason = get_return_reason_from_history(history)

    if current_message_is_reason:
        return_reason = user_message
    elif is_waiting_for_return_reason(history):
        return_reason = user_message
    else:
        return_reason = prior_reason

    if not order_id:
        return {
            "response": "I can help start a return. What is your Bookly order ID?",
            "action": "clarifying_question",
            "tool_called": None,
            "intent": "return_request",
        }

    if return_reason:
        result = create_return_request(order_id, return_reason)

        return {
            "response": result["message"],
            "action": "create_return_request",
            "tool_called": "create_return_request",
            "intent": "return_request",
        }

    return {
        "response": "Thanks. What is the reason for the return?",
        "action": "clarifying_question",
        "tool_called": None,
        "intent": "return_request",
    }


def run_bookly_agent(user_message: str, history: list[dict] | None = None):
    """
    Bookly's support-agent orchestration layer.

    - Python controls workflow state, missing fields, and tool calls.
    - OpenAI helps interpret long-tail conversational phrasing.
    - Policy answers come from controlled Bookly content.
    """
    history = history or []

    current_order_id = extract_order_id(user_message)
    waiting_for_order_id = is_waiting_for_order_id(history)
    waiting_for_return_reason = is_waiting_for_return_reason(history)

    # Deterministic handling for follow-up turns.
    if waiting_for_return_reason:
        return run_return_flow(
            user_message=user_message,
            history=history,
            current_order_id=current_order_id,
        )

    if waiting_for_order_id and current_order_id:
        last_assistant_message = get_last_assistant_message(history) or ""

        if "start a return" in last_assistant_message.lower():
            return run_return_flow(
                user_message=user_message,
                history=history,
                current_order_id=current_order_id,
            )

        return run_order_status_flow(current_order_id)

    # Deterministic coverage for common status language.
    if looks_like_order_status_request(user_message):
        return run_order_status_flow(current_order_id)

    classification = classify_customer_message(user_message, history)
    intent = classification["intent"]

    if intent == "order_status":
        return run_order_status_flow(current_order_id)

    if intent == "return_request":
        return run_return_flow(
            user_message=user_message,
            history=history,
            current_order_id=current_order_id,
        )

    if intent == "shipping_policy":
        return {
            "response": get_bookly_policy_answer("shipping"),
            "action": "policy_lookup",
            "tool_called": "get_bookly_policy_answer",
            "intent": "shipping_policy",
        }

    if intent == "return_policy":
        return {
            "response": get_bookly_policy_answer("returns"),
            "action": "policy_lookup",
            "tool_called": "get_bookly_policy_answer",
            "intent": "return_policy",
        }

    if intent == "refund_policy":
        return {
            "response": get_bookly_policy_answer("refunds"),
            "action": "policy_lookup",
            "tool_called": "get_bookly_policy_answer",
            "intent": "refund_policy",
        }

    if intent == "password_reset":
        return {
            "response": get_bookly_policy_answer("password_reset"),
            "action": "policy_lookup",
            "tool_called": "get_bookly_policy_answer",
            "intent": "password_reset",
        }

    return {
        "response": (
            "I can help with order tracking, returns, refunds, shipping, and "
            "password resets. What would you like help with?"
        ),
        "action": "fallback",
        "tool_called": None,
        "intent": "other",
    }