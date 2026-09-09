from .models import (
    OrderStatusHistory,
    RefundStatusHistory,
)


def record_order_status_change(
    order,
    previous_status,
    new_status,
    changed_by,
    note="",
):
    if previous_status == new_status:
        return None

    return OrderStatusHistory.objects.create(
        order=order,
        previous_status=previous_status or "",
        new_status=new_status,
        changed_by=changed_by,
        note=note,
    )


def record_refund_status_change(
    refund,
    new_status,
    actor=None,
    note="",
):
    previous_event = (
        RefundStatusHistory.objects
        .filter(refund=refund)
        .order_by("-created_at", "-id")
        .first()
    )

    if previous_event and previous_event.status == new_status:
        return None

    return RefundStatusHistory.objects.create(
        refund=refund,
        status=new_status,
        actor=actor,
        note=note,
    )
