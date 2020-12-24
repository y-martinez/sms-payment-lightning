from django.shortcuts import render
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

def home(request):
    """View function for home page of site."""

    return render(request, 'app/home.html')