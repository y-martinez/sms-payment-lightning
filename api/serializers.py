from django.conf import settings
from rest_framework import serializers
from app.models import Wallet, User, Payment
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
        balance_btc = wallet.balance * settings.CRYPTO_CONSTANTS["SAT_TO_BTC_FACTOR"]
        return balance_btc * current_rate["rate"]["value"]


class UserSerializer(serializers.ModelSerializer):
    wallet = WalletSerializer(read_only=True)

    def create(self, validated_data):
        # call create_user on user object. Without  this
        # the password will be stored in plain text.
        user = User.objects.create_user(**validated_data)
        return user

    class Meta:
        model = User
        fields = ["phone_number", "wallet"]
        extra_kwargs = {"password": {"write_only": True}}


class PaymentSerializer(serializers.ModelSerializer):
    payer = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field="username",
        error_messages={"does_not_exist": "The user {value} does not exist"},
    )
    payee = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field="username",
        error_messages={"does_not_exist": "The user {value} does not exist"},
    )

    class Meta:
        model = Payment
        fields = ["description", "value", "payer", "payee"]
        extra_kwargs = {
            "value": {
                "error_messages": {
                    "min_value": "The payment amount should be greater than or equal to 100 satoshis"
                }
            }
        }

    def validate(self, data):
        if data["payer"] == data["payee"]:
            raise serializers.ValidationError(
                {"payer": "Payee must be different from payer"}
            )
        if data["payer"].wallet.balance < data["value"]:
            raise serializers.ValidationError({"payer": "Payer has insufficient funds"})
        return data
