from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from accounts.permissions import IsSupplier

from .models import Supplier

from .services import (
    SupplierDashboardService,
)

from .dashboard_serializers import (
    SupplierDashboardSerializer,
)


# ==========================================================
# SUPPLIER DASHBOARD
# ==========================================================

class SupplierDashboardView(
    generics.RetrieveAPIView
):
    """
    Supplier dashboard.

    Returns dashboard information only
    for the authenticated supplier.
    """

    permission_classes = [
        IsAuthenticated,
        IsSupplier,
    ]

    serializer_class = (
        SupplierDashboardSerializer
    )

    queryset = (
        Supplier.objects
        .select_related(
            "user",
        )
        .prefetch_related(
            "products",
            "products__inventory",
            
        )
    )


    # ==========================================================
    # GET AUTHENTICATED SUPPLIER
    # ==========================================================

    def get_object(self):

        try:

            return (
                self.get_queryset()
                .get(
                    user=self.request.user,
                )
            )

        except Supplier.DoesNotExist:

            raise NotFound(
                "Supplier profile does not exist."
            )


    # ==========================================================
    # GET DASHBOARD
    # ==========================================================

    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):

        supplier = self.get_object()

        service = SupplierDashboardService(
            supplier
        )


        # ======================================================
        # STATISTICS
        # ======================================================

        product_statistics = (
            service.get_product_statistics()
        )

        order_statistics = (
            service.get_order_statistics()
        )

        payment_statistics = (
            service.get_payment_statistics()
        )


        # ======================================================
        # DASHBOARD DATA
        # ======================================================

        data = {

            "supplier": {

                "id":
                    supplier.id,

                "name":
                    supplier.name,

                "company":
                    supplier.company,

                "email":
                    supplier.email,

                "phone":
                    supplier.phone,

            },


            "statistics": {

                **product_statistics,

                **order_statistics,

                **payment_statistics,

            },


            "notifications":
                service.get_notifications(),


            "recent_activity":
                service.get_recent_activity(),


            "recent_products":
                service.get_recent_products(),


            "recent_orders":
                service.get_recent_orders(),


            "low_stock_alerts":
                service.get_low_stock_alerts(),


            "inventory_summary":
                service.get_inventory_summary(),


            "sales_overview":
                service.get_sales_overview(),

        }


        # ======================================================
        # SERIALIZE
        # ======================================================

        serializer = self.get_serializer(
            instance=data
        )



        # ======================================================
        # RESPONSE
        # ======================================================

        return Response(
            {
                "success": True,
                "dashboard": serializer.data,
            }
        )
        

