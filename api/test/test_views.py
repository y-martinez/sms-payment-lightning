from django.urls import reverse
from nose.tools import eq_
from rest_framework.test import APITestCase
from unittest.mock import patch
from rest_framework import status
from .factories import WalletFactory
from ..serializers import WalletSerializer
from app.models import Wallet


class TestWalletListTestCase(APITestCase):
    def setUp(self):
        WalletFactory.create_batch(5)
        self.all_wallets = WalletSerializer(Wallet.objects.all(), many=True)
        self.url = reverse("wallet-list")
        self.expected_wallet_data = {"address": WalletFactory.generate_address()}

    def test_get_all_wallets(self):
        response = self.client.get(self.url)
        eq_(response.status_code, status.HTTP_200_OK)
        eq_(response.data, self.all_wallets.data)

    @patch("app.lnd_client.requests.get")
    def test_create_wallet(self, mock_method):

        mock_method.return_value.json.return_value = self.expected_wallet_data
        response = self.client.post(self.url)
        eq_(response.status_code, status.HTTP_201_CREATED)
        exists = Wallet.objects.filter(
            address=self.expected_wallet_data["address"]
        ).exists()
        eq_(exists, True)


class TestWalletDetailTestCase(APITestCase):
    def setUp(self):
        self.wallet = WalletFactory.create()
        self.expected_wallet_data = {"address": WalletFactory.generate_address()}

    def test_get_wallet_by_address(self):
        url = reverse("wallet-detail", kwargs={"address": self.wallet.address})

        response = self.client.get(url)
        eq_(response.status_code, status.HTTP_200_OK)

        self.wallet.address = "wallet"
        url = reverse("wallet-detail", kwargs={"address": self.wallet.address})

        response = self.client.get(url)
        eq_(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_wallet_by_addres(self):
        url = reverse("wallet-detail", kwargs={"address": self.wallet.address})

        response = self.client.delete(url)
        eq_(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(url)
        eq_(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch("app.lnd_client.requests.get")
    def test_update_wallet_by_address(self, mock_method):
        url = reverse("wallet-detail", kwargs={"address": self.wallet.address})

        mock_method.return_value.json.return_value = self.expected_wallet_data
        response = self.client.put(url)

        eq_(response.status_code, status.HTTP_200_OK)
