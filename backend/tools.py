ORDERS = {
    "BK-1001": {
        "order_id": "BK-1001",
        "status": "shipped",
        "carrier": "UPS",
        "tracking_number": "1Z999BOOKLY",
        "eta": "Friday",
        "eligible_for_return": True,
    },
    "BK-1002": {
        "order_id": "BK-1002",
        "status": "processing",
        "carrier": None,
        "tracking_number": None,
        "eta": "Monday",
        "eligible_for_return": False,
    },
}


def get_order_status(order_id: str):
    """
    Mock Bookly order-management-system lookup.
    In production, this would call an OMS or ecommerce API.
    """
    order = ORDERS.get(order_id.upper())

    if not order:
        return {
            "found": False,
            "message": "No order found for that order ID.",
        }

    return {
        "found": True,
        "order": order,
    }


def create_return_request(order_id: str, reason: str):
    """
    Mock Bookly returns-system action.
    In production, this would create a return in an ecommerce or CRM system.
    """
    order = ORDERS.get(order_id.upper())

    if not order:
        return {
            "success": False,
            "message": "I couldn't find that order ID. Could you double-check it?",
        }

    if not order["eligible_for_return"]:
        return {
            "success": False,
            "message": (
                f"Order {order_id.upper()} is not currently eligible for a return. "
                "It may still be processing or outside the return window."
            ),
        }

    return {
        "success": True,
        "return_id": f"RET-{order_id.upper()}",
        "message": (
            f"Your return request has been created. "
            f"Your return ID is RET-{order_id.upper()}. "
            "A prepaid return label has been emailed to you."
        ),
        "reason": reason,
    }