from django.test import TestCase
from django.forms.models import model_to_dict
from nose.tools import eq_, ok_
from .factories import WalletFactory
from ..serializers import WalletSerializer


class TestWalletSerializer(TestCase):

    def setUp(self):
        self.wallet_data = model_to_dict(WalletFactory.build())

    def test_serializer_with_empty_data(self):
        serializer = WalletSerializer(data={})
        eq_(serializer.is_valid(), False)
        serializer = WalletSerializer(data={"s":"s"})
        eq_(serializer.is_valid(), False)
        
    def test_serializer_with_valid_data(self):
        serializer = WalletSerializer(data=self.wallet_data)
        ok_(serializer.is_valid())