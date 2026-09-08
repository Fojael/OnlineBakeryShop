from .models import OrderStatusHistory


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
