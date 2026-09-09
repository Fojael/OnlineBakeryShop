from django.db.models import Count, Sum

from orders.models import Order, OrderItem
from products.models import Product


def _products_by_ids(product_ids, limit=8):
    if not product_ids:
        return Product.objects.none()

    ordering = {product_id: index for index, product_id in enumerate(product_ids)}
    products = Product.objects.filter(
        id__in=product_ids,
        is_available=True,
        stock_quantity__gt=0,
    )
    return sorted(products, key=lambda product: ordering.get(product.id, limit))[:limit]


def build_customer_recommendations(user=None, product_id=None, limit=8):
    delivered_items = OrderItem.objects.filter(
        order__status=Order.STATUS_DELIVERED,
    )

    popular_ids = list(
        delivered_items.values("product_id")
        .annotate(total_units=Sum("quantity"))
        .order_by("-total_units", "product_id")
        .values_list("product_id", flat=True)[:limit]
    )

    frequently_purchased_ids = []
    if user and user.is_authenticated:
        frequently_purchased_ids = list(
            delivered_items.filter(order__customer=user)
            .values("product_id")
            .annotate(purchase_count=Count("order_id", distinct=True))
            .order_by("-purchase_count", "product_id")
            .values_list("product_id", flat=True)[:limit]
        )

    related_ids = []
    if product_id:
        product = Product.objects.filter(id=product_id).first()
        if product:
            related_ids = list(
                Product.objects.filter(
                    category=product.category,
                    is_available=True,
                    stock_quantity__gt=0,
                )
                .exclude(id=product.id)
                .order_by("-featured", "-created_at")
                .values_list("id", flat=True)[:limit]
            )

    return {
        "recommended_products": _products_by_ids(
            frequently_purchased_ids or popular_ids,
            limit,
        ),
        "frequently_purchased": _products_by_ids(
            frequently_purchased_ids,
            limit,
        ),
        "popular_products": _products_by_ids(popular_ids, limit),
        "related_products": _products_by_ids(related_ids, limit),
    }