from django.shortcuts import render
from .serializers import *
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated,AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from common.pagination import CustomPagination
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.timezone import now as djnow, localtime, make_aware
from django.contrib.auth import get_user_model
from common.permission import has_permission
from .models import PermissionEnum
# Create your views here.
class BaseModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]


    @has_permission(PermissionEnum.MANAGE_USERS.value) 
    def list(self, request, *args, **kwargs):
        paginator = CustomPagination()
        page = paginator.paginate_queryset(self.queryset, request)
        serializer = self.get_serializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @has_permission(PermissionEnum.MANAGE_USERS.value)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @has_permission(PermissionEnum.MANAGE_USERS.value)
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    @has_permission(PermissionEnum.MANAGE_USERS.value)
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

User = get_user_model()

class UserViewSet(BaseModelViewSet):
    queryset = User.objects.filter(is_deleted=False).order_by("-id")
    serializer_class = UserSerializer
    search_fields = ['email']

    def get_permissions(self):
        if self.action in ['register', 'login']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'detail': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = self.queryset.get(email=email)
            if not user.is_active:
                return Response({'detail': 'Account is not active'}, status=status.HTTP_401_UNAUTHORIZED)
            if not user.check_password(password):
                return Response({'detail': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)
            user.last_login = djnow()
            user.save(update_fields=["last_login"])
            return Response({
                'detail': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role.name if user.role else None,
                }
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    

