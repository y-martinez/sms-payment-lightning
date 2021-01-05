from rest_framework import viewsets, status, generics, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from app.services import LndRestClient, get_current_rate
from app.models import Wallet, User
from api.serializers import (
    WalletSerializer,
    WalletSerializerBalance,
    UserSerializer,
)

client = LndRestClient()


class GetWalletBalance(generics.RetrieveAPIView):
    lookup_field = "address"
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializerBalance

    def get(self, request, *args, **kwargs):
        response = get_current_rate(self)

        if "error" in response.keys():
            return Response(
                data={"error": response["error"]}, status=response["status_code"]
            )
        else:
            response = {
                "rate": {"code": "USD", "value": response["bpi"]["USD"]["rate_float"]}
            }

        instance = self.get_object()
        serializer = self.get_serializer(instance, context=response)
        return Response(serializer.data)


class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    lookup_field = "address"

    def get_paginated_response(self, data):
        return Response(data)

    @action(methods=["post"], detail=False)
    def new_address(self, request):
        response = client.new_address()
        if "error" in response.keys():
            return Response(
                data={"error": response["error"]}, status=response["status_code"]
            )
        else:
            return Response(response)

    def create(self, request, *args, **kwargs):
        response = self.new_address(self)
        if response.status_code >= 400:
            return response

        serializer = self.get_serializer(data=response.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):

        response = self.new_address(self)
        if response.status_code >= 400:
            return response

        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=response.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class UserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):

    lookup_field = "phone_number"
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_paginated_response(self, data):
        return Response(data)

    def perform_create(self, serializer, wallet_created):

        serializer.save(
            username=self.request.data["phone_number"],
            phone_number=self.request.data["phone_number"],
            wallet=wallet_created,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        response = WalletViewSet.as_view({"post": "create"})(
            request=self.request._request
        )

        if response.status_code >= 400:
            return response

        wallet_created = Wallet.objects.get(address=response.data["address"])

        self.perform_create(serializer, wallet_created)
        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
