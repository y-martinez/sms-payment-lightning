import requests
from django.urls import reverse
from unittest.mock import patch, Mock
from nose.tools import eq_
from rest_framework.test import APITestCase
from rest_framework import status
from ..serializers import InvoiceSerializer
from .factories import UserFactory, InvoiceFactory
from .data_fake import data_info_payreq, data_invoice_paid, data_invoice_not_paid
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

    def _mock_response(self, content, status_code=200):
        mock = Mock()
        mock.content = content
        mock.ok = status_code >= 200 and status_code < 400
        mock.status_code = status_code
        mock.json.return_value = mock.content or '""'
        return mock

    @patch("app.services.requests.get")
    @patch("app.services.requests.post")
    def test_invoice_data_ok(self, mock_payinvoice, mock_info_payreq):

        mock_resp_info = self._mock_response(
            status_code=status.HTTP_200_OK, content=data_info_payreq
        )
        mock_resp_invoice = self._mock_response(
            status_code=status.HTTP_201_CREATED, content=data_invoice_paid
        )

        mock_info_payreq.return_value = mock_resp_info
        mock_info_payreq.raise_for_status = status.HTTP_200_OK

        mock_payinvoice.return_value = mock_resp_invoice
        mock_payinvoice.raise_for_status = status.HTTP_201_CREATED

        total_invoice_amount = int(data_invoice_paid["payment_route"]["total_amt"])

        response = self.client.post(self.url, self.data_to_pay, format="json")
        eq_(response.status_code, status.HTTP_201_CREATED)

        user_payer_updated = User.objects.get(pk=self.user_payer.id).wallet.balance
        payer_balance_expected = self.user_payer.wallet.balance - total_invoice_amount

        eq_(user_payer_updated, payer_balance_expected)

    @patch("app.services.requests.get")
    def test_invoice_data_not_ok_info(self, mock_info_payreq):

        mock_resp = self._mock_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=data_invoice_not_paid["error_invoice_payreq_malformatted"],
        )
        mock_info_payreq.return_value = mock_resp
        mock_info_payreq.side_effect = requests.exceptions.HTTPError(response=mock_resp)

        response = self.client.post(self.url, self.data_to_pay, format="json")
        eq_(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        eq_(
            response.data["error"],
            data_invoice_not_paid["error_invoice_payreq_malformatted"]["message"],
        )

        mock_resp = self._mock_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=data_invoice_not_paid["error_invoice_checksum"],
        )
        mock_info_payreq.return_value = mock_resp
        mock_info_payreq.side_effect = requests.exceptions.HTTPError(response=mock_resp)

        response = self.client.post(self.url, self.data_to_pay, format="json")
        eq_(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        eq_(
            response.data["error"],
            data_invoice_not_paid["error_invoice_checksum"]["message"],
        )

    @patch("app.services.requests.get")
    @patch("app.services.requests.post")
    def test_invoice_data_not_ok_payinvoice(self, mock_payinvoice, mock_info_payreq):

        mock_resp_info = self._mock_response(
            status_code=status.HTTP_200_OK, content=data_info_payreq
        )
        mock_info_payreq.return_value = mock_resp_info
        mock_info_payreq.raise_for_status = status.HTTP_200_OK

        # Already paid

        mock_resp_invoice = self._mock_response(
            status_code=status.HTTP_200_OK,
            content=data_invoice_not_paid["error_invoice_paid"],
        )

        mock_payinvoice.return_value = mock_resp_invoice
        mock_payinvoice.raise_for_status = status.HTTP_200_OK

        response = self.client.post(self.url, self.data_to_pay, format="json")

        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)
        eq_(
            response.data["error"],
            data_invoice_not_paid["error_invoice_paid"]["payment_error"],
        )

        ########

        # Invoice incorrect

        mock_resp_invoice = self._mock_response(
            status_code=status.HTTP_200_OK,
            content=data_invoice_not_paid["error_invoice_incorrect"],
        )

        mock_payinvoice.return_value = mock_resp_invoice
        mock_payinvoice.raise_for_status = status.HTTP_200_OK

        response = self.client.post(self.url, self.data_to_pay, format="json")

        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)
        eq_(
            response.data["error"],
            data_invoice_not_paid["error_invoice_incorrect"]["payment_error"],
        )

        ########

        # Invoice in transition

        mock_resp_invoice = self._mock_response(
            status_code=status.HTTP_200_OK,
            content=data_invoice_not_paid["error_invoice_in_transition"],
        )

        mock_payinvoice.return_value = mock_resp_invoice
        mock_payinvoice.raise_for_status = status.HTTP_200_OK

        response = self.client.post(self.url, self.data_to_pay, format="json")

        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)
        eq_(
            response.data["error"],
            data_invoice_not_paid["error_invoice_in_transition"]["payment_error"],
        )

        ########

        # Invoice no route

        mock_resp_invoice = self._mock_response(
            status_code=status.HTTP_200_OK,
            content=data_invoice_not_paid["error_invoice_no_route"],
        )

        mock_payinvoice.return_value = mock_resp_invoice
        mock_payinvoice.raise_for_status = status.HTTP_200_OK

        response = self.client.post(self.url, self.data_to_pay, format="json")

        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)
        eq_(
            response.data["error"],
            data_invoice_not_paid["error_invoice_no_route"]["payment_error"],
        )

        ########

        # Invoice expired

        mock_resp_invoice = self._mock_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=data_invoice_not_paid["error_invoice_expired"],
        )

        mock_payinvoice.return_value = mock_resp_invoice
        mock_payinvoice.side_effect = requests.exceptions.HTTPError(
            response=mock_resp_invoice
        )

        response = self.client.post(self.url, self.data_to_pay, format="json")

        eq_(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        eq_(
            response.data["error"],
            data_invoice_not_paid["error_invoice_expired"]["message"],
        )

        ########

    def test_get_all_invoice(self):
        response = self.client.get(self.url)
        eq_(response.status_code, status.HTTP_200_OK)
        eq_(response.data, self.all_payments.data)
