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
        current_rate = self.context["rate"]
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
    TYPE_OF_PAYMENT_CHOICES = (("usd", "usd"), ("btc", "btc"), ("sat", "sat"))
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

    type_of_payment = serializers.ChoiceField(
        choices=TYPE_OF_PAYMENT_CHOICES,
        write_only=True,
        required=True,
        error_messages={
            "required": "You must specify a type of payment",
            "null": "You must specify a type of payment",
            "invalid_choice": "You must specify a valid type of payment",
        },
    )

    class Meta:
        model = Payment
        fields = [
            "description",
            "value",
            "payer",
            "payee",
            "type_of_payment",
            "created_at",
        ]
        read_only_fields = ["created_at"]
        extra_kwargs = {
            "value": {
                "error_messages": {
                    "min_value": "The payment amount should be greater than or equal to 100 satoshis",
                    "max_value": "The payment amount should be less than or equal to 100000000 satoshis",
                }
            }
        }

    def to_internal_value(self, instance):
        factor = settings.CRYPTO_CONSTANTS["BTC_TO_SAT_FACTOR"]
        if "value" in instance.keys() and "type_of_payment" in instance.keys():
            if isinstance(instance["value"], float) and isinstance(
                instance["type_of_payment"], str
            ):
                if instance["type_of_payment"] == "btc":
                    instance["value"] = instance["value"] * factor
                    instance["value"] = float(
                        round(instance["value"], settings.CRYPTO_CONSTANTS["PRECISION"])
                    )
                    instance["value"] = int(instance["value"])

                if instance["type_of_payment"] == "usd":
                    current_rate = self.context["rate"]
                    instance["value"] = instance["value"] * factor
                    instance["value"] = (
                        instance["value"] / current_rate["rate"]["value"]
                    )
                    instance["value"] = float(
                        round(instance["value"], settings.CRYPTO_CONSTANTS["PRECISION"])
                    )
                    instance["value"] = int(instance["value"])
        return super().to_internal_value(instance)

    def create(self, validated_data):
        validated_data.pop("type_of_payment", None)
        return super().create(validated_data)

    def validate(self, data):
        if data["payer"] == data["payee"]:
            raise serializers.ValidationError(
                {"payer": "Payee must be different from payer"}
            )
        if data["payer"].wallet.balance < data["value"]:
            raise serializers.ValidationError({"payer": "Payer has insufficient funds"})
        return data
