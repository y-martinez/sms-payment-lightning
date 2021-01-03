from django.test import TestCase
from django.forms.models import model_to_dict
from nose.tools import eq_, ok_
from .factories import WalletFactory, UserFactory
from ..serializers import WalletSerializer, WalletSerializerBalance, UserSerializer


class TestWalletSerializer(TestCase):
    def setUp(self):
        self.wallet_data = model_to_dict(WalletFactory.build())

    def test_wallet_serializer_with_empty_data(self):
        serializer = WalletSerializer(data={})
        eq_(serializer.is_valid(), False)
        serializer = WalletSerializer(data={"s": "s"})
        eq_(serializer.is_valid(), False)

    def test_wallet_serializer_with_valid_data(self):
        serializer = WalletSerializer(data=self.wallet_data)
        ok_(serializer.is_valid())


class TestWalletBalanceSerializer(TestCase):
    def setUp(self):
        self.wallet_data = model_to_dict(WalletFactory.build())

    def test_balance_serializer_with_empty_data(self):
        serializer = WalletSerializerBalance(data={})
        eq_(not serializer.is_valid(), False)

    def test_balance_serializer_with_valid_data(self):
        serializer = WalletSerializer(data=self.wallet_data)
        ok_(serializer.is_valid())


class TestUserSerializer(TestCase):
    def setUp(self):
        self.user = UserFactory.build()
        self.user_data = model_to_dict(self.user)
        self.user_data["phone_number"] = str(self.user.phone_number)

    def test_serializer_with_empty_data(self):
        serializer = UserSerializer(data={})
        eq_(serializer.is_valid(), False)

    def test_serializer_with_valid_data(self):
        serializer = UserSerializer(data=self.user_data)
        ok_(serializer.is_valid())
