from django.urls import path, re_path, include, reverse_lazy
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from .views import WalletViewSet, GetWalletBalance, UserViewSet


router = DefaultRouter()
router.register(r"wallets", WalletViewSet)
router.register(r"users", UserViewSet)

urlpatterns = [
    path("api/v1/", include(router.urls)),
    re_path(
        r"^api/v1/wallets/(?P<address>[^/.]+)/balance/$",
        GetWalletBalance.as_view(),
        name="wallet-balance",
    ),
    path("api-token-auth/", views.obtain_auth_token),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    re_path(r"^$", RedirectView.as_view(url=reverse_lazy("api-root"), permanent=False)),
]
