from rest_framework import serializers


class InventoryDashboardSerializer(
    serializers.Serializer
):

    total_products = serializers.IntegerField()

    total_stock = serializers.IntegerField()

    in_stock = serializers.IntegerField()

    low_stock = serializers.IntegerField()

    out_of_stock = serializers.IntegerField()