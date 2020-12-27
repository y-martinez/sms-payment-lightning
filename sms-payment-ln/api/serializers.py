from rest_framework import serializers
from app.models import Wallet

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['address','balance']
        read_only_fields = ['balance']