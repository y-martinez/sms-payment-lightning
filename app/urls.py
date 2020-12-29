from django.urls import path
from app import views

urlpatterns = [path("home", views.home, name="home")]
