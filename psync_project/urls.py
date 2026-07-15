from django.contrib import admin
from django.urls import include, path

from psnv.views import SignUpView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/signup/", SignUpView.as_view(), name="signup"),
    path("accounts/", include("django.contrib.auth.urls")),  # login/logout/password reset
    path("", include("psnv.urls")),
]
