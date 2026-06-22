from __future__ import annotations

import hashlib
import re
from datetime import date, timedelta
from typing import Any

ORDER_ID_PATTERN = re.compile(r"^BK-\d{4}$")

CARRIERS = [
    "UPS",
    "USPS",
    "FedEx",
]

BOOK_TITLES = [
    "The Midnight Library",
    "Tomorrow, and Tomorrow, and Tomorrow",
    "Project Hail Mary",
    "Yellowface",
    "The Night Circus",
    "Sea of Tranquility",
    "The Song of Achilles",
    "Remarkably Bright Creatures",
]

FORMATS = [
    "Hardcover",
    "Paperback",
    "Ebook",
]

RETURN_REASONS = {
    "damaged": "Item arrived damaged",
    "wrong_item": "Wrong item received",
    "wrong_format": "Wrong format ordered",
    "duplicate": "Duplicate purchase",
    "changed_mind": "Changed my mind",
    "gift": "Gift return",
    "late_delivery": "Arrived too late",
    "other": "Other",
}


def normalize_order_id(value: str | None) -> str | None:
    """
    Normalizes flexible user input such as:
    - bk 1234
    - BK1234
    - bk-1234

    Into:
    - BK-1234
    """
    if not value:
        return None

    compact = re.sub(r"[^a-zA-Z0-9]", "", value).upper()

    if not re.fullmatch(r"BK\d{4}", compact):
        return None

    return f"BK-{compact[2:]}"


def is_valid_order_id(value: str | None) -> bool:
    normalized = normalize_order_id(value)
    return bool(normalized and ORDER_ID_PATTERN.fullmatch(normalized))


def extract_order_ids(text: str) -> list[str]:
    """
    Finds all Bookly-like order IDs in a message.

    Supports:
    - BK-1001
    - BK 1001
    - bk1001
    """
    matches = re.findall(r"\bBK[\s-]?\d{4}\b", text, flags=re.IGNORECASE)

    normalized_ids: list[str] = []

    for match in matches:
        normalized = normalize_order_id(match)
        if normalized and normalized not in normalized_ids:
            normalized_ids.append(normalized)

    return normalized_ids


def _stable_number(order_id: str) -> int:
    digest = hashlib.sha256(order_id.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def _tracking_number(order_id: str, carrier: str) -> str:
    stable_number = _stable_number(order_id)

    if carrier == "UPS":
        return f"1Z{stable_number % 10_000_000_000:010d}"

    if carrier == "USPS":
        return f"9400{stable_number % 10_000_000_000_000_000_000:018d}"

    return f"FDX{stable_number % 10_000_000_000:010d}"


def _days_ago(days: int) -> str:
    return (date.today() - timedelta(days=days)).isoformat()


def _days_from_now(days: int) -> str:
    return (date.today() + timedelta(days=days)).strftime("%A, %B %-d")


def get_order_details(order_id: str) -> dict[str, Any]:
    """
    Returns deterministic mock order data for every valid BK-#### ID.

    The same order ID always returns the same data, which makes demos,
    tests, and multi-turn conversations consistent.
    """
    normalized_id = normalize_order_id(order_id)

    if not normalized_id:
        return {
            "found": False,
            "error": "invalid_order_id",
            "message": "That does not look like a valid Bookly order ID.",
        }

    number = _stable_number(normalized_id)

    title = BOOK_TITLES[number % len(BOOK_TITLES)]
    format_name = FORMATS[(number // 7) % len(FORMATS)]
    carrier = CARRIERS[(number // 11) % len(CARRIERS)]

    lifecycle_bucket = number % 6

    # 0: processing
    # 1: shipped
    # 2: shipped, delayed
    # 3: delivered recently
    # 4: delivered long ago
    # 5: canceled
    if lifecycle_bucket == 0:
        status = "processing"
        shipment_status = "not_shipped"
        ordered_days_ago = 1 + (number % 3)
        delivery_date = None
        eta = _days_from_now(2)
        tracking_number = None
        return_eligible = False
        cancellation_eligible = True
        address_change_eligible = True
        refund_status = None

    elif lifecycle_bucket == 1:
        status = "shipped"
        shipment_status = "in_transit"
        ordered_days_ago = 3 + (number % 4)
        delivery_date = None
        eta = _days_from_now(1 + (number % 3))
        tracking_number = _tracking_number(normalized_id, carrier)
        return_eligible = False
        cancellation_eligible = False
        address_change_eligible = False
        refund_status = None

    elif lifecycle_bucket == 2:
        status = "shipped"
        shipment_status = "delayed"
        ordered_days_ago = 6 + (number % 3)
        delivery_date = None
        eta = _days_from_now(2 + (number % 4))
        tracking_number = _tracking_number(normalized_id, carrier)
        return_eligible = False
        cancellation_eligible = False
        address_change_eligible = False
        refund_status = None

    elif lifecycle_bucket == 3:
        status = "delivered"
        shipment_status = "delivered"
        ordered_days_ago = 10 + (number % 8)
        delivery_date = _days_ago(1 + (number % 5))
        eta = None
        tracking_number = _tracking_number(normalized_id, carrier)
        return_eligible = True
        cancellation_eligible = False
        address_change_eligible = False
        refund_status = None

    elif lifecycle_bucket == 4:
        status = "delivered"
        shipment_status = "delivered"
        ordered_days_ago = 48 + (number % 30)
        delivery_date = _days_ago(35 + (number % 20))
        eta = None
        tracking_number = _tracking_number(normalized_id, carrier)
        return_eligible = False
        cancellation_eligible = False
        address_change_eligible = False
        refund_status = "completed"

    else:
        status = "canceled"
        shipment_status = "not_shipped"
        ordered_days_ago = 2 + (number % 10)
        delivery_date = None
        eta = None
        tracking_number = None
        return_eligible = False
        cancellation_eligible = False
        address_change_eligible = False
        refund_status = "pending"

    price_cents = 1499 + (number % 2200)

    return {
        "found": True,
        "order": {
            "order_id": normalized_id,
            "status": status,
            "shipment_status": shipment_status,
            "book_title": title,
            "format": format_name,
            "carrier": carrier if tracking_number else None,
            "tracking_number": tracking_number,
            "ordered_at": _days_ago(ordered_days_ago),
            "delivered_at": delivery_date,
            "eta": eta,
            "return_eligible": return_eligible,
            "cancellation_eligible": cancellation_eligible,
            "address_change_eligible": address_change_eligible,
            "refund_status": refund_status,
            "price_cents": price_cents,
        },
    }


def get_order_status(order_id: str) -> dict[str, Any]:
    return get_order_details(order_id)


def check_return_eligibility(order_id: str) -> dict[str, Any]:
    result = get_order_details(order_id)

    if not result["found"]:
        return result

    order = result["order"]

    if order["return_eligible"]:
        return {
            "found": True,
            "eligible": True,
            "order": order,
            "message": (
                f"Order {order['order_id']} is eligible for a return within "
                "30 days of delivery."
            ),
        }

    if order["status"] == "processing":
        message = (
            f"Order {order['order_id']} is still processing, so it is not "
            "eligible for a return yet. You may be able to cancel it instead."
        )
    elif order["status"] == "shipped":
        message = (
            f"Order {order['order_id']} is still in transit. Once it arrives, "
            "you can start a return if it is within the return window."
        )
    elif order["status"] == "canceled":
        message = f"Order {order['order_id']} has already been canceled."
    else:
        message = (
            f"Order {order['order_id']} is outside Bookly's 30-day return "
            "window."
        )

    return {
        "found": True,
        "eligible": False,
        "order": order,
        "message": message,
    }


def create_return_request(order_id: str, reason: str) -> dict[str, Any]:
    eligibility = check_return_eligibility(order_id)

    if not eligibility.get("found"):
        return eligibility

    if not eligibility.get("eligible"):
        return {
            "success": False,
            "message": eligibility["message"],
            "order": eligibility["order"],
        }

    order = eligibility["order"]
    return_id = f"RET-{order['order_id']}-{_stable_number(reason) % 1000:03d}"

    return {
        "success": True,
        "return_id": return_id,
        "order": order,
        "reason": reason,
        "message": (
            f"Your return request for {order['book_title']} has been created. "
            f"Your return ID is {return_id}. A prepaid shipping label has been "
            "emailed to you."
        ),
    }


def cancel_order(order_id: str) -> dict[str, Any]:
    result = get_order_details(order_id)

    if not result["found"]:
        return result

    order = result["order"]

    if not order["cancellation_eligible"]:
        if order["status"] == "shipped":
            message = (
                f"Order {order['order_id']} has already shipped, so it cannot "
                "be canceled. You can start a return after delivery."
            )
        elif order["status"] == "delivered":
            message = (
                f"Order {order['order_id']} has already been delivered, so it "
                "cannot be canceled. I can check whether it is eligible for a return."
            )
        elif order["status"] == "canceled":
            message = f"Order {order['order_id']} was already canceled."
        else:
            message = f"Order {order['order_id']} cannot be canceled right now."

        return {
            "success": False,
            "order": order,
            "message": message,
        }

    return {
        "success": True,
        "order": order,
        "message": (
            f"Order {order['order_id']} has been canceled. A refund of "
            f"${order['price_cents'] / 100:.2f} will be returned to the "
            "original payment method within 5–7 business days."
        ),
    }


def update_shipping_address(order_id: str, new_address: str) -> dict[str, Any]:
    result = get_order_details(order_id)

    if not result["found"]:
        return result

    order = result["order"]

    if not order["address_change_eligible"]:
        if order["status"] == "shipped":
            message = (
                f"Order {order['order_id']} has already shipped, so Bookly can "
                "no longer change the delivery address. You may be able to "
                "request a delivery hold directly with the carrier."
            )
        else:
            message = (
                f"Order {order['order_id']} is no longer eligible for an "
                "address change."
            )

        return {
            "success": False,
            "order": order,
            "message": message,
        }

    return {
        "success": True,
        "order": order,
        "new_address": new_address,
        "message": (
            f"The shipping address for order {order['order_id']} has been "
            "updated successfully."
        ),
    }


def create_missing_package_claim(order_id: str) -> dict[str, Any]:
    result = get_order_details(order_id)

    if not result["found"]:
        return result

    order = result["order"]

    if order["status"] != "delivered":
        return {
            "success": False,
            "order": order,
            "message": (
                f"Order {order['order_id']} is not marked as delivered yet, "
                "so a missing-package claim cannot be started."
            ),
        }

    claim_id = f"CLAIM-{order['order_id']}-{_stable_number(order['book_title']) % 1000:03d}"

    return {
        "success": True,
        "claim_id": claim_id,
        "order": order,
        "message": (
            f"I started a missing-package claim for order {order['order_id']}. "
            f"Your claim ID is {claim_id}. A Bookly support specialist will "
            "follow up within 1–2 business days."
        ),
    }


def get_refund_status(order_id: str) -> dict[str, Any]:
    result = get_order_details(order_id)

    if not result["found"]:
        return result

    order = result["order"]
    refund_status = order["refund_status"]

    if refund_status == "completed":
        message = (
            f"The refund for order {order['order_id']} was completed and sent "
            "to the original payment method."
        )
    elif refund_status == "pending":
        message = (
            f"A refund for order {order['order_id']} is pending and should "
            "appear within 5–7 business days."
        )
    else:
        message = (
            f"I do not see a refund in progress for order {order['order_id']}."
        )

    return {
        "found": True,
        "order": order,
        "refund_status": refund_status,
        "message": message,
    }


def get_bookly_policy_answer(policy_topic: str) -> str:
    policies = {
        "shipping": (
            "Bookly offers standard shipping in 3–5 business days and "
            "expedited shipping in 1–2 business days."
        ),
        "returns": (
            "Bookly accepts returns within 30 days of delivery for books in "
            "resellable condition."
        ),
        "refunds": (
            "Refunds are sent to the original payment method within 5–7 "
            "business days after Bookly receives the returned item."
        ),
        "password_reset": (
            "You can reset your password from the Bookly login page by "
            "selecting “Forgot password.”"
        ),
        "address_changes": (
            "Bookly can update a shipping address only while an order is still "
            "processing and has not shipped."
        ),
        "cancellations": (
            "Bookly can cancel an order only while it is still processing and "
            "before it ships."
        ),
    }

    return policies.get(
        policy_topic,
        (
            "I can help with orders, tracking, returns, refunds, shipping, "
            "address changes, cancellations, and password resets."
        ),
    )