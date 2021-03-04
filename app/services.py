import requests
from django.urls import reverse
from django.conf import settings
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from typing import Dict
from blockcypher import (
    subscribe_to_address_webhook as subscribe_address_webhook,
    unsubscribe_from_webhook,
    list_webhooks as list_of_webhooks,
)
from app import messages


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


def get_current_rate(code="USD") -> Dict:
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


class SmsClient:
    def __init__(self):
        account_sid = settings.TWILIO["ACCOUNT_ID"]
        auth_token = settings.TWILIO["AUTH_TOKEN"]
        self.client_twilio = Client(account_sid, auth_token)

    def _make_sms(self, messages):
        response_twiml = MessagingResponse()
        for message, phone_number in messages:
            response_twiml.message(body=message, to=phone_number)
        return response_twiml

    def create(self, from_phone_number):
        sms = self._make_sms([(messages.USER_CREATED, from_phone_number)])
        return str(sms)

    def reload(self, from_phone_number, content_sms, step="start"):
        sms = self._make_sms(
            [(messages.USER_RELOAD_FUNDS[step] % content_sms, from_phone_number)]
        )
        return str(sms)

    def pay(self, from_phone_number, content_sms, type):
        sms = self._make_sms(
            [(messages.USER_PAYMENT_INVOICE[type] % content_sms, from_phone_number)]
        )
        return str(sms)

    def transfer(
        self, from_phone_number, to_phone_number, content_sms_payer, content_sms_payee
    ):
        sms = self._make_sms(
            [
                (
                    messages.USER_PAYMENT["successful_payer"] % content_sms_payer,
                    from_phone_number,
                ),
                (
                    messages.USER_PAYMENT["successful_payee"] % content_sms_payee,
                    to_phone_number,
                ),
            ]
        )
        return str(sms)

    def balance(self, from_phone_number, content_sms):
        sms = self._make_sms([(messages.USER_BALANCE % content_sms, from_phone_number)])
        return str(sms)

    def help(self, from_phone_number):
        sms = self._make_sms([(messages.HELP_MESSAGE, from_phone_number)])
        return str(sms)

    def error(self, message, from_phone_number, error_message):
        sms = self._make_sms(
            [(messages.ERROR_MESSAGES[error_message], from_phone_number)]
        )
        return str(sms)


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
            return response.json()
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

    def info_payreq(self, payment_request) -> Dict:
        try:
            response = requests.get(
                f"{self.endpoint}/v1/payreq/{payment_request}",
                headers=self.auth,
                verify=self.cert,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            if "error" in errh.response.json().keys():
                return {
                    "error": errh.response.json()["message"],
                    "status_code": errh.response.status_code,
                }
            return {
                "error": errh.response.text,
                "status_code": errh.response.status_code,
            }
        except requests.exceptions.RequestException:
            return {
                "error": f"Unable to connect to {self.endpoint}",
                "status_code": 500,
            }
        data_payment = response.json()

        if "payment_error" in data_payment.keys():
            return {
                "error": data_payment["payment_error"],
                "status_code": 400,
            }
        return response.json()

    def pay_invoice(self, payment_request) -> Dict:
        try:
            response = requests.post(
                f"{self.endpoint}/v1/channels/transactions",
                json={"payment_request": payment_request},
                headers=self.auth,
                verify=self.cert,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            if "error" in errh.response.json().keys():
                return {
                    "error": errh.response.json()["message"],
                    "status_code": errh.response.status_code,
                }
            return {
                "error": errh.response.text,
                "status_code": errh.response.status_code,
            }
        except requests.exceptions.RequestException:
            return {
                "error": f"Unable to connect to {self.endpoint}",
                "status_code": 500,
            }
        data_payment = response.json()
        if "payment_error" in data_payment.keys():
            return {
                "error": data_payment["payment_error"],
                "status_code": 400,
            }
        return response.json()
