from django.shortcuts import render
from django.conf import settings
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from common.permission import has_permission
from common.pagination import CustomPagination
from common.utils import *
from .serializers import *
import pymongo
# Create your views here.
client = pymongo.MongoClient(settings.MONGODB_URI)
db = client[settings.MONGODB_DATABASE]
collection = db[settings.MONGODB_COLLECTION]

class BaseModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]


    @has_permission(PermissionEnum.WATCH_VIDEO.value) 
    def list(self, request, *args, **kwargs):
        client = pymongo.MongoClient(settings.MONGODB_URI)
        db = client[settings.MONGODB_DATABASE]
        collection = db[settings.MONGODB_COLLECTION]
        user_id = request.user.id
        documents = list(collection.find(
            {'is_deleted': False, 'uploaderId': user_id},
            {'title': 1, 'description': 1, 'uploadDate': 1}
        ).sort('uploadDate', -1))

        for doc in documents:
            doc['id'] = str(doc['_id'])

        paginator = CustomPagination()
        page = paginator.paginate_queryset(documents, request)
        serializer = self.get_serializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


    @has_permission(PermissionEnum.UPLOAD_VIDEO.value)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @has_permission(PermissionEnum.UPLOAD_VIDEO.value)
    def update(self, request, *args, **kwargs):
        client = pymongo.MongoClient(settings.MONGODB_URI)
        db = client[settings.MONGODB_DATABASE]
        collection = db[settings.MONGODB_COLLECTION]

        _id = kwargs.get("pk")
        instance = collection.find_one({"_id": ObjectId(_id)})
        if not instance:
            return Response({"detail": "Video not found"}, status=status.HTTP_404_NOT_FOUND)

        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial, context={"object_id": _id})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    @has_permission(PermissionEnum.DELETE_VIDEO.value)
    def destroy(self, request, *args, **kwargs):
        client = pymongo.MongoClient(settings.MONGODB_URI)
        db = client[settings.MONGODB_DATABASE]
        collection = db[settings.MONGODB_COLLECTION]
        _id = kwargs.get("pk")
        collection.find_one_and_update({'_id': ObjectId(_id)}, {'$set': {'is_deleted': True}})
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class VideoViewSet(BaseModelViewSet):
    queryset = list(collection.find())
    serializer_class = VideoSerializer

    
