from django.urls import reverse
from nose.tools import eq_
from rest_framework.test import APITestCase
from unittest.mock import patch
from rest_framework import status
from .factories import UserFactory

data_of_webhook = {
    "block_hash": "0000000000000012db3eb9d21199f801e43be828817d6f6d60681c7979c5bbb3",
    "block_height": 1902015,
    "block_index": 4,
    "hash": "d1b6fb7ba9e638c1c243c14a2adde0f34f04ab9b2e0e6c0a94b0ec43a4a3a5ca",
    "addresses": [
        "2NGAaoZc59jss3WkjfarS8oM5MLvcpkxC9e",
        "tb1qwatu5c240fnuk5yryqx3cxmzmaj7c7eydzwred",
        "tb1qxmjhkm8lnyp52yr4d02k8ta0928h4650agntfv",
    ],
    "total": 5820758368,
    "fees": 16691,
    "size": 136,
    "preference": "low",
    "relayed_by": "46.101.165.206:18333",
    "confirmed": "2021-01-02T20:14:21Z",
    "received": "2021-01-02T20:09:04.164Z",
    "ver": 2,
    "lock_time": 1902014,
    "double_spend": False,
    "vin_sz": 1,
    "vout_sz": 2,
    "confirmations": 1,
    "inputs": [
        {
            "prev_hash": "ea928b5090058fd2d2a55a22c5fc068ae8a56c5c39738192647675aaa4bace62",
            "output_index": 0,
            "script": "1600146647bd94f69ab58dde2333276c80dd9cdcac7693",
            "output_value": 5820775059,
            "sequence": 4294967294,
            "addresses": ["2NGAaoZc59jss3WkjfarS8oM5MLvcpkxC9e"],
            "script_type": "pay-to-script-hash",
            "age": 1902014,
        }
    ],
    "outputs": [
        {
            "value": 5819156582,
            "script": "001436e57b6cff99034510756bd563afaf2a8f7aea8f",
            "addresses": [],
            "script_type": "pay-to-witness-pubkey-hash",
        },
        {
            "value": 1601786,
            "script": "00147757ca61557a67cb5083200d1c1b62df65ec7b24",
            "addresses": ["tb1qwatu5c240fnuk5yryqx3cxmzmaj7c7eydzwred"],
            "script_type": "pay-to-witness-pubkey-hash",
        },
    ],
}

data_list_webhooks = [
    {
        "address": "15qx9ug952GWGTNn7Uiv6vode4RcGrRemh",
        "callback_errors": 0,
        "confirmations": 6,
        "event": "confirmed-tx",
        "filter": "event=confirmed-tx&addr=15qx9ug952GWGTNn7Uiv6vode4RcGrRemh",
        "id": "bcaf7c39-9a7f-4e8b-8ba4-23b3c1806039",
        "token": "TOKEN",
        "url": "https://example.com/callbacks/new-tx",
    }
]


class TestRefill(APITestCase):
    def setUp(self):
        self.user_data = UserFactory.create()
        self.url_incoming = reverse("wallet-refill")
        self.url_outcoming = reverse(
            "wallet-refill", kwargs={"address": self.user_data.wallet.address}
        )

    @patch("app.services.list_of_webhooks")
    @patch("app.services.unsubscribe_from_webhook")
    def test_response_of_webhook_blockcypher_ok(self, mock_unsubscribe, mock_list):

        data_of_webhook["outputs"][0]["addresses"].append(self.user_data.wallet.address)

        data_list_webhooks[0]["address"] = self.user_data.wallet.address

        mock_unsubscribe.return_value = True
        mock_list.return_value = data_list_webhooks

        response = self.client.post(
            self.url_incoming, data=data_of_webhook, format="json"
        )
        eq_(response.status_code, status.HTTP_200_OK)

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

        mock_subscribe.return_value = "bcaf7c39-9a7f-4e8b-8ba4-23b3c1806039"

        response = self.client.get(self.url_outcoming)
        eq_(response.status_code, status.HTTP_200_OK)

    @patch("app.services.subscribe_address_webhook")
    def test_create_webhook_to_refill_address_not_ok(self, mock_subscribe):

        mock_subscribe.return_value = "bcaf7c39-9a7f-4e8b-8ba4-23b3c1806039"

        response = self.client.get(self.url_incoming)
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)
