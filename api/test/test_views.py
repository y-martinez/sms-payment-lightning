from django.urls import reverse
from nose.tools import eq_, ok_
from rest_framework.test import APITestCase
from unittest.mock import patch
from rest_framework import status
from .factories import WalletFactory
from ..serializers import WalletSerializer
from app.models import Wallet
from decimal import Decimal


class TestAddressTestCase(APITestCase):
    def setUp(self):
        self.url = reverse("wallet-new-address")
        self.expected_wallet_data = {"address": WalletFactory.generate_address()}
        self.expected_wallet_data_not_ok = [
            {
                "error": "Unable to connect www.example.com:9876",
                "status_code": 500,
            },
            {"error": "Not found", "status_code": 404},
        ]

    @patch("app.services.requests.get")
    def test_get_new_address_is_ok(self, mock_method):
        mock_method.return_value.json.return_value = self.expected_wallet_data
        response = self.client.post(self.url)
        eq_(response.status_code, status.HTTP_200_OK)

    @patch("app.services.requests.get")
    def test_get_new_address_is_not_ok(self, mock_method):
        for error in self.expected_wallet_data_not_ok:
            mock_method.return_value.json.return_value = error
            response = self.client.post(self.url)
            ok_(response.status_code != status.HTTP_200_OK)


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

    @patch("app.services.requests.get")
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

    @patch("app.services.requests.get")
    def test_update_wallet_by_address(self, mock_method):
        url = reverse("wallet-detail", kwargs={"address": self.wallet.address})

        mock_method.return_value.json.return_value = self.expected_wallet_data
        response = self.client.put(url)

        eq_(response.status_code, status.HTTP_200_OK)


class TestWalletBalanceTestCase(APITestCase):
    def setUp(self):
        self.wallet = WalletFactory.create()
        self.url = reverse("wallet-balance", kwargs={"address": self.wallet.address})
        self.expected_rate_data = {
            "time": {
                "updated": "Dec 31, 2020 21:00:00 UTC",
                "updatedISO": "2020-12-31T21:00:00+00:00",
                "updateduk": "Dec 31, 2020 at 21:00 GMT",
            },
            "disclaimer": "This data was produced from the CoinDesk Bitcoin Price\
                Index (USD). Non-USD currency data converted using hourly conversion\
                    rate from openexchangerates.org",
            "bpi": {
                "USD": {
                    "code": "USD",
                    "rate": "21,306.29",
                    "description": "United States Dollar",
                    "rate_float": 21306.29,
                }
            },
        }

        self.balance_usd_expected = self.wallet.balance * Decimal(
            self.expected_rate_data["bpi"]["USD"]["rate_float"]
        )

        self.expected_rate_data_not_ok = {
            "error": "Unable to connect www.apibtc.com",
            "status_code": 500,
        }

    @patch("app.services.requests.get")
    def test_get_balance_by_address(self, mock_method):
        mock_method.return_value.json.return_value = self.expected_rate_data
        response = self.client.get(self.url)
        eq_(response.status_code, status.HTTP_200_OK)
        ok_(response.data["balance_usd"], self.balance_usd_expected)

    @patch("app.services.requests.get")
    def test_get_balance_by_address_not_ok(self, mock_method):
        mock_method.return_value.json.return_value = self.expected_rate_data_not_ok
        response = self.client.get(self.url)
        ok_(response.status_code != status.HTTP_200_OK)
