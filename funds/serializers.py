from rest_framework import serializers
from funds.models import Fund, FundPrice


class FundPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundPrice
        fields = ['date', 'closing_price']


class FundSerializer(serializers.ModelSerializer):
    prices = FundPriceSerializer(many=True)

    class Meta:
        model = Fund
        fields = ['fund_code', 'name', 'prices']
