from django.urls import reverse
from nose.tools import ok_, eq_
from rest_framework.test import APITestCase
from rest_framework import status
from .factories import WalletFactory


class TestWalletListTestCase(APITestCase):
    def setUp(self):
        WalletFactory.create_batch(5)
        self.url = reverse("wallet-list")
        self.wallet_data = WalletFactory.generate_address()

    def test_get_all_wallets(self):
        response = self.client.get(self.url)
        eq_(response.status_code, status.HTTP_200_OK)

    # ESTO NO SIRVE...
    # def test_create_wallet(self):
    #     response = self.client.post(self.url)
    #     eq_(response.status_code, status.HTTP_201_CREATED)


class TestWalletDetailTestCase(APITestCase):
    def setUp(self):
        self.wallet = WalletFactory.create()

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
