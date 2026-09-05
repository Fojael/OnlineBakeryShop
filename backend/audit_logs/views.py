from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsAdmin

from .models import AuditLog
from .serializers import AuditLogSerializer


class AdminAuditLogListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = AuditLogSerializer

    def get_queryset(self):
        return AuditLog.objects.select_related("actor")
