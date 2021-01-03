from django.urls import reverse
from nose.tools import eq_
from rest_framework.test import APITestCase
from unittest.mock import patch
from rest_framework import status
from .factories import UserFactory, WalletFactory
from ..serializers import UserSerializer
from app.models import User
from factory import build


class TestUserListTestCase(APITestCase):
    """
    Tests /users list operations.
    """

    def setUp(self):
        UserFactory.create_batch(5)
        self.url = reverse("user-list")
        self.all_users = UserSerializer(User.objects.all(), many=True)
        self.user_data = build(dict, FACTORY_CLASS=UserFactory)
        self.expected_wallet_data = {"address": WalletFactory.generate_address()}

    def test_get_all_users(self):
        response = self.client.get(self.url)
        eq_(response.status_code, status.HTTP_200_OK)
        eq_(response.data, self.all_users.data)

    def test_create_user_with_no_data(self):
        response = self.client.post(self.url)
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("app.services.requests.get")
    def test_create_user_with_valid_data(self, mock_method):
        mock_method.return_value.json.return_value = self.expected_wallet_data
        response = self.client.post(self.url, self.user_data)
        eq_(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(phone_number=response.data.get("phone_number"))
        eq_(user.phone_number, self.user_data.get("phone_number"))


class TestUserDetailTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory.create()
        self.url = reverse(
            "user-detail", kwargs={"phone_number": self.user.phone_number}
        )

    def test_get_user_by_phone_number(self):

        response = self.client.get(self.url)
        eq_(response.status_code, status.HTTP_200_OK)

        self.user.phone_number = "+584125554433"
        url = reverse("user-detail", kwargs={"phone_number": self.user.phone_number})

        response = self.client.get(url)
        eq_(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_user_by_phone_number(self):

        response = self.client.delete(self.url)
        eq_(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(self.url)
        eq_(response.status_code, status.HTTP_404_NOT_FOUND)
