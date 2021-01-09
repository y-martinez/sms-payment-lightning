from django.urls import reverse
from django.conf import settings
from unittest.mock import patch
from nose.tools import eq_
from rest_framework.test import APITestCase
from rest_framework import status
from ..serializers import PaymentSerializer
from .factories import UserFactory, PaymentFactory
from .data_fake import data_rate
from app.models import User, Payment
from factory import build


class TestPaymentView(APITestCase):
    def setUp(self):
        PaymentFactory.create_batch(5)

        self.all_payments = PaymentSerializer(Payment.objects.all(), many=True)
        self.url = reverse("payment-list")
        self.user_payer = UserFactory.create()
        self.user_payee = UserFactory.create()

        self.data_to_pay = build(dict, FACTORY_CLASS=PaymentFactory)
        self.data_to_pay["payer"] = str(self.user_payer.phone_number)
        self.data_to_pay["payee"] = str(self.user_payee.phone_number)
        self.data_to_pay["type_of_payment"] = ""

        self.expected_rate_data = data_rate

    @patch("app.services.requests.get")
    def test_payment_with_usd_data_ok(self, mock_method):
        mock_method.return_value.json.return_value = self.expected_rate_data

        data_to_pay = self.data_to_pay
        amount_sat = data_to_pay["value"]
        data_to_pay["type_of_payment"] = "usd"
        amount_btc = amount_sat * settings.CRYPTO_CONSTANTS["SAT_TO_BTC_FACTOR"]
        data_to_pay["value"] = amount_btc * self.expected_rate_data["bpi"]["USD"]["rate_float"]

        response = self.client.post(self.url, data=data_to_pay,format="json")
        eq_(response.status_code, status.HTTP_201_CREATED)
        
        user_payer_updated = User.objects.get(pk=self.user_payer.id)
        user_payee_updated = User.objects.get(pk=self.user_payee.id)

        payer_balance_expected = self.user_payer.wallet.balance - amount_sat
        payee_balance_expected = self.user_payee.wallet.balance + amount_sat

        eq_(payer_balance_expected, user_payer_updated.wallet.balance)
        eq_(payee_balance_expected, user_payee_updated.wallet.balance)



    def test_payment_with_btc_data_ok(self):
        data_to_pay = self.data_to_pay
        amount_sat = data_to_pay["value"]
        data_to_pay["type_of_payment"] = "btc"
        data_to_pay["value"] = (
            data_to_pay["value"] * settings.CRYPTO_CONSTANTS["SAT_TO_BTC_FACTOR"]
        )

        data_to_pay["value"] = float(round(data_to_pay["value"], 8))

        response = self.client.post(self.url, data=data_to_pay, format="json")
        eq_(response.status_code, status.HTTP_201_CREATED)

        user_payer_updated = User.objects.get(pk=self.user_payer.id)
        user_payee_updated = User.objects.get(pk=self.user_payee.id)

        payer_balance_expected = self.user_payer.wallet.balance - amount_sat
        payee_balance_expected = self.user_payee.wallet.balance + amount_sat

        eq_(payer_balance_expected, user_payer_updated.wallet.balance)
        eq_(payee_balance_expected, user_payee_updated.wallet.balance)

    def test_payment_with_satoshis_data_ok(self):
        data_to_pay = self.data_to_pay
        data_to_pay["type_of_payment"] = "sat"
        amount_sat = data_to_pay["value"]

        response = self.client.post(self.url, data=self.data_to_pay , format="json")
        eq_(response.status_code, status.HTTP_201_CREATED)

        user_payer_updated = User.objects.get(pk=self.user_payer.id)
        user_payee_updated = User.objects.get(pk=self.user_payee.id)

        payer_balance_expected = self.user_payer.wallet.balance - amount_sat
        payee_balance_expected = self.user_payee.wallet.balance + amount_sat

        eq_(payer_balance_expected, user_payer_updated.wallet.balance)
        eq_(payee_balance_expected, user_payee_updated.wallet.balance)

    def test_payment_with_satatoshis_data_not_ok(self):
        data_to_pay = self.data_to_pay
        data_to_pay["type_of_payment"] = "sat"

        amount_sat = self.user_payer.wallet.balance

        data_to_pay["value"] = amount_sat + 1
        response = self.client.post(self.url, data=data_to_pay, format="json")
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)
        eq_(response.data["payer"][0], "Payer has insufficient funds")

        data_to_pay["payee"] = data_to_pay["payer"]
        response = self.client.post(self.url, data=data_to_pay, format="json")
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)
        eq_(response.data["payer"][0], "Payee must be different from payer")

        data_to_pay["value"] = 0
        response = self.client.post(self.url, data=data_to_pay, format="json")
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)
        eq_(
            response.data["value"][0],
            "The payment amount should be greater than or equal to 100 satoshis",
        )

        data_to_pay["value"] = 100000001
        response = self.client.post(self.url, data=data_to_pay, format="json")
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)
        eq_(
            response.data["value"][0],
            "The payment amount should be less than or equal to 100000000 satoshis",
        )

        payer_not_exist = "+584169009614"
        payee_not_exist = "+584169009615"
        data_to_pay["payer"] = payer_not_exist
        data_to_pay["payee"] = payee_not_exist
        response = self.client.post(self.url, data=data_to_pay, format="json")
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)
        eq_(response.data["payer"][0], f"The user {payer_not_exist} does not exist")
        eq_(response.data["payee"][0], f"The user {payee_not_exist} does not exist")

    def test_payment_with_blank_data(self):

        response = self.client.post(self.url, data={}, format="json")
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)
        eq_(response.data["type_of_payment"][0], "You must specify a type of payment")
        eq_(response.data["value"][0], "This field is required.")
        eq_(response.data["payer"][0], "This field is required.")
        eq_(response.data["payee"][0], "This field is required.")

        response = self.client.post(self.url, data={"type_of_payment":"test"}, format="json")
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)
        eq_(response.data["type_of_payment"][0], "You must specify a valid type of payment")

    def test_get_all_payments(self):
        response = self.client.get(self.url)
        eq_(response.status_code, status.HTTP_200_OK)
        eq_(response.data, self.all_payments.data)
