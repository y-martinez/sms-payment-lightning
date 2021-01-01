from rest_framework import serializers
from app.models import Wallet
from decimal import Decimal
from datetime import datetime


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ["address", "balance"]
        read_only_fields = ["balance"]


class WalletSerializerBalance(serializers.ModelSerializer):
    balance_usd = serializers.SerializerMethodField()
    date_updated = serializers.SerializerMethodField()

    class Meta:
        model = Wallet
        fields = ["balance", "balance_usd", "date_updated"]
        read_only_fields = ["balance"]

    def get_date_updated(self, wallet):
        return datetime.now().strftime("%I:%M %p, %d-%m-%Y")

    def get_balance_usd(self, wallet):
        current_rate = self.context
        return wallet.balance * Decimal(current_rate["rate"]["value"])
