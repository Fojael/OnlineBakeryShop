from .models import AuditLog


def record_audit(
    *,
    actor,
    action,
    obj,
    old_value=None,
    new_value=None,
):
    return AuditLog.objects.create(
        actor=actor,
        action=action,
        object_type=obj.__class__.__name__,
        object_id=str(obj.pk),
        old_value=old_value,
        new_value=new_value,
    )
