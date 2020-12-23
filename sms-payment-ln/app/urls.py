from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin
from app import views

urlpatterns = [
    path('home', views.home, name='home')

]