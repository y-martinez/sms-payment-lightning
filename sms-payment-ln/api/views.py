import importlib

from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.views import APIView
from rest_framework.response import Response
from app.lnd_client import LndRestClient
from app.models import Wallet
from api.serializers import WalletSerializer

client = LndRestClient()
class Test(APIView):
    
    def get(self,request,format=None):
        response = client.newaddress()
        if 'error' in response.keys():
            return Response(response['error'],status=response['status_code'])
        else:
            return Response(response)

class WalletViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer