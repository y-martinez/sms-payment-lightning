from django.urls import reverse
from unittest.mock import patch
from nose.tools import eq_
from rest_framework.test import APITestCase
from rest_framework import status
from ..serializers import InvoiceSerializer
from .factories import UserFactory, InvoiceFactory
from .data_fake import data_info_payreq, data_invoice_paid
from app.models import User, Invoice
from factory import build


class TestInvoiceView(APITestCase):
    def setUp(self):
        InvoiceFactory.create_batch(5)
        self.url = reverse("invoice-list")
        self.user_payer = UserFactory.create()
        self.all_payments = InvoiceSerializer(Invoice.objects.all(), many=True)

        self.data_to_pay = build(dict, FACTORY_CLASS=InvoiceFactory)
        self.data_to_pay["payer"] = str(self.user_payer.phone_number)

    @patch("app.services.requests.get")
    @patch("app.services.requests.post")
    def test_invoice_data_ok(self, mock_payinvoice, mock_info_payreq):
        mock_info_payreq.return_value.json.return_value = data_info_payreq
        mock_payinvoice.return_value.json.return_value = data_invoice_paid
        total_invoice_amount = int(data_invoice_paid["payment_route"]["total_amt"])

        response = self.client.post(self.url, self.data_to_pay, format="json")
        eq_(response.status_code, status.HTTP_201_CREATED)

        user_payer_updated = User.objects.get(pk=self.user_payer.id).wallet.balance
        payer_balance_expected = self.user_payer.wallet.balance - total_invoice_amount

        eq_(user_payer_updated, payer_balance_expected)

    def test_get_all_invoice(self):
        response = self.client.get(self.url)
        eq_(response.status_code, status.HTTP_200_OK)
        eq_(response.data, self.all_payments.data)
