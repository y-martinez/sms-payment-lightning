from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("app.urls")),
    path("", include("api.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)