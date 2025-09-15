from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'video', VideoViewSet, basename='video')

urlpatterns = [
    path('api/v1/', include(router.urls)),
]