from django.urls import reverse
from nose.tools import eq_
from rest_framework.test import APITestCase
from rest_framework import status
from ..serializers import PaymentSerializer
from .factories import UserFactory, PaymentFactory
from app.models import User, Payment
from factory import build


class TestPaymentSatoshis(APITestCase):
    def setUp(self):
        PaymentFactory.create_batch(5)

        self.all_payments = PaymentSerializer(Payment.objects.all(), many=True)
        self.url = reverse("payment-list")
        self.user_payer = UserFactory.create()
        self.user_payee = UserFactory.create()

        self.data_to_pay = build(dict, FACTORY_CLASS=PaymentFactory)
        self.data_to_pay["payer"] = str(self.user_payer.phone_number)
        self.data_to_pay["payee"] = str(self.user_payee.phone_number)

    def test_payment_with_data_ok(self):
        amount_sat = self.data_to_pay["value"]

        response = self.client.post(self.url, data=self.data_to_pay)
        eq_(response.status_code, status.HTTP_201_CREATED)

        user_payer_updated = User.objects.get(pk=self.user_payer.id)
        user_payee_updated = User.objects.get(pk=self.user_payee.id)

        payer_balance_expected = self.user_payer.wallet.balance - amount_sat
        payee_balance_expected = self.user_payee.wallet.balance + amount_sat

        eq_(payer_balance_expected, user_payer_updated.wallet.balance)
        eq_(payee_balance_expected, user_payee_updated.wallet.balance)

    def test_payment_with_data_not_ok(self):

        response = self.client.post(self.url, data={})
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)
        eq_(response.data["value"][0], "This field is required.")
        eq_(response.data["payer"][0], "This field is required.")
        eq_(response.data["payee"][0], "This field is required.")

        amount_sat = self.user_payer.wallet.balance

        self.data_to_pay["value"] = amount_sat + 1
        response = self.client.post(self.url, data=self.data_to_pay)
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)
        eq_(response.data["payer"][0], "Payer has insufficient funds")

        self.data_to_pay["payee"] = self.data_to_pay["payer"]
        response = self.client.post(self.url, data=self.data_to_pay)
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)
        eq_(response.data["payer"][0], "Payee must be different from payer")

        self.data_to_pay["value"] = 0
        response = self.client.post(self.url, data=self.data_to_pay)
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)
        eq_(
            response.data["value"][0],
            "The payment amount should be greater than or equal to 100 satoshis",
        )

        payer_not_exist = "+584169009614"
        payee_not_exist = "+584169009615"
        self.data_to_pay["payer"] = payer_not_exist
        self.data_to_pay["payee"] = payee_not_exist
        response = self.client.post(self.url, data=self.data_to_pay)
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)
        eq_(response.data["payer"][0], f"The user {payer_not_exist} does not exist")
        eq_(response.data["payee"][0], f"The user {payee_not_exist} does not exist")

    def test_get_all_payments(self):
        response = self.client.get(self.url)
        eq_(response.status_code, status.HTTP_200_OK)
        eq_(response.data, self.all_payments.data)
