import requests
from django.urls import reverse
from django.conf import settings
from typing import Dict
from blockcypher import (
    subscribe_to_address_webhook as subscribe_address_webhook,
    unsubscribe_from_webhook,
    list_webhooks as list_of_webhooks,
)


def list_webhooks() -> Dict:
    return list_of_webhooks(
        api_key=settings.BLOCKCYPHER["TOKEN"], coin_symbol=settings.BLOCKCYPHER["COIN"]
    )


def unsubscribe_webhook_address(address) -> bool:
    webhooks = list_webhooks()
    for webhook in webhooks:
        if webhook["address"] == address:
            return unsubscribe_from_webhook(
                webhook_id=webhook["id"],
                api_key=settings.BLOCKCYPHER["TOKEN"],
                coin_symbol=settings.BLOCKCYPHER["COIN"],
            )
    return False


def subscribe_to_address_webhook(request, address) -> str:
    full_url = request.build_absolute_uri(reverse("wallet-refill"))
    return subscribe_address_webhook(
        callback_url=full_url,
        subscription_address=address,
        event="confirmed-tx",
        api_key=settings.BLOCKCYPHER["TOKEN"],
        coin_symbol=settings.BLOCKCYPHER["COIN"],
    )


def get_current_rate(self, code="USD") -> Dict:
    endpoint = "https://api.coindesk.com/v1/bpi/currentprice"
    try:
        response = requests.get(f"{endpoint}/{code}.json")
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return {
            "error": f"Unable to connect to {endpoint}",
            "status_code": 500,
        }
    return response.json()


class LndRestClient:
    def __init__(self):
        endpoint = settings.LND_REST["ENDPOINT"]
        endpoint = endpoint[:-1] if endpoint.endswith("/") else endpoint
        endpoint = (
            "https://" + endpoint if not endpoint.startswith("http") else endpoint
        )
        self.endpoint = endpoint

        self.auth = {"Grpc-Metadata-macaroon": settings.LND_REST["MACAROON"]}
        self.cert = settings.LND_REST["CERT"]

    def new_address(self) -> Dict:
        try:
            response = requests.get(
                f"{self.endpoint}/v1/newaddress", headers=self.auth, verify=self.cert
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            return {
                "error": errh.response.text,
                "status_code": errh.response.status_code,
            }
        except requests.exceptions.RequestException:
            return {
                "error": f"Unable to connect to {self.endpoint}",
                "status_code": 500,
            }

        return response.json()
