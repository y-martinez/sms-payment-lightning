import importlib

from rest_framework import generics, viewsets, mixins
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.views import APIView
from rest_framework.decorators import action
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


class WalletViewSet( mixins.CreateModelMixin,viewsets.GenericViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer

    @action(methods=['post'], detail=False)
    def newAddress(self,request):
        response = client.new_address()
        if 'error' in response.keys():
            return Response(data = {"error": response['error']}, status=response['status_code'])
        else:
            return Response(response)

    def create(self, request, *args,**kwargs):
        response = self.newAddress(self)
        if response.status_code >= 400:
            return response
        else:
            mutable = request.POST._mutable
            request.POST._mutable = True
            request.POST['address'] = response.data['address']
            request.POST._mutable = mutable
        return super().create(request,args,kwargs)