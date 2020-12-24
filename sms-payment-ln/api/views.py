import importlib

from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.views import APIView
from rest_framework.response import Response
from app.lnd_client import LndRestClient

client = LndRestClient()
class Test(APIView):
    
    def get(self,request,format=None):
        response = client.newaddress()
        if 'error' in response.keys():
            return Response(response['error'],status=response['status_code'])
        else:
            return Response(response)
