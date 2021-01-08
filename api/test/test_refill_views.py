from django.urls import reverse
from nose.tools import eq_
from rest_framework.test import APITestCase
from unittest.mock import patch
from rest_framework import status
from .factories import UserFactory
from .data_fake import data_of_webhook, data_list_webhooks
from app.models import User


class TestRefill(APITestCase):
    def setUp(self):
        self.user_data = UserFactory.create()
        self.url_incoming = reverse("wallet-refill")
        self.url_outcoming = reverse(
            "wallet-refill", kwargs={"address": self.user_data.wallet.address}
        )
        self.id_webhook = "bcaf7c39-9a7f-4e8b-8ba4-23b3c1806039"

    @patch("app.services.list_of_webhooks")
    @patch("app.services.unsubscribe_from_webhook")
    def test_response_of_webhook_blockcypher_ok(self, mock_unsubscribe, mock_list):

        data_of_webhook["outputs"][0]["addresses"].append(self.user_data.wallet.address)
        data_list_webhooks[0]["address"] = self.user_data.wallet.address
        incoming_sat = data_of_webhook["outputs"][0]["value"]

        mock_unsubscribe.return_value = True
        mock_list.return_value = data_list_webhooks

        response = self.client.post(
            self.url_incoming, data=data_of_webhook, format="json"
        )

        eq_(response.status_code, status.HTTP_200_OK)

        user = User.objects.get(phone_number=self.user_data.phone_number)
        expected_balance = self.user_data.wallet.balance + incoming_sat

        eq_(expected_balance, user.wallet.balance)

    @patch("app.services.list_of_webhooks")
    @patch("app.services.unsubscribe_from_webhook")
    def test_response_of_webhook_blockcypher_not_ok(self, mock_unsubscribe, mock_list):

        mock_unsubscribe.return_value = True
        mock_list.return_value = data_list_webhooks

        response = self.client.post(
            self.url_incoming, data=data_of_webhook, format="json"
        )
        eq_(response.status_code, status.HTTP_304_NOT_MODIFIED)

    @patch("app.services.subscribe_address_webhook")
    def test_create_webhook_to_refill_address_ok(self, mock_subscribe):

        mock_subscribe.return_value = self.id_webhook

        response = self.client.get(self.url_outcoming)
        eq_(response.status_code, status.HTTP_200_OK)

    @patch("app.services.subscribe_address_webhook")
    def test_create_webhook_to_refill_address_not_ok(self, mock_subscribe):

        mock_subscribe.return_value = self.id_webhook

        response = self.client.get(self.url_incoming)
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)
