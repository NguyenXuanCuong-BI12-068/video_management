from django.urls import path, include
from .views import *
from . import auth_google
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'user', UserViewSet, basename='user')

urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('auth/login-sso/', auth_google.login_sso, name='login-sso'),
]