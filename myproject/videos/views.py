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
import cloudinary.uploader
import cloudinary.api
import ffmpeg
# Create your views here.

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
            {'is_deleted': False, 'uploaderId': user_id}
        ).sort('uploadDate', -1))

        for doc in documents:
            doc['id'] = str(doc['_id'])

        paginator = CustomPagination()
        page = paginator.paginate_queryset(documents, request)
        serializer = self.get_serializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


    @has_permission(PermissionEnum.UPLOAD_VIDEO.value)
    def create(self, request, *args, **kwargs):
        video_uploaded = self.process_video(request.data['file'], request.data['title'])
        serializer = self.get_serializer(
            data=request.data,
            context={
                'request': request,
                'file': video_uploaded['url'],
                'duration': video_uploaded['duration'],
                'size': video_uploaded['size'],
                'resolution': video_uploaded['resolution'],
            }
        )
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
        response = collection.find_one_and_update({'_id': ObjectId(_id)}, {'$set': {'is_deleted': True}})
        public_id = response['title']
        cloud_deleted = cloudinary.uploader.destroy(public_id, resource_type ="video", type="upload")

        return Response(cloud_deleted, status=status.HTTP_200_OK)
    
    def process_video(self, video_file, video_id):
        client = pymongo.MongoClient(settings.MONGODB_URI)
        db = client[settings.MONGODB_DATABASE]
        collection = db["video-information"]

        upload_result = cloudinary.uploader.upload_large(
            video_file,
            resource_type="video",
            public_id=video_id,
            chunk_size=10 * 1024 * 1024,
            eager=[
                {"width": 1920, "height": 1080, "crop": "scale", "video_codec": "h264"},
                {"width": 1920, "height": 1080, "crop": "scale", "quality": 30, "video_codec": "h264"},
                {"width": 1920, "height": 1080, "crop": "scale", "quality": 10, "video_codec": "h264"},
            ],
            eager_async=False
        )

        thumb_url = cloudinary.CloudinaryImage(video_id).video_thumbnail(
            width=300, height=200, resource_type="video"
        )

        result = {
            "id": video_id,
            "url": upload_result['secure_url'],
            "duration": upload_result['duration'],
            "size": upload_result['bytes'],
            "resolution": f"{upload_result['width']}x{upload_result['height']}",
            "width": upload_result['width'],
            "height": upload_result['height'],
            "formats": {
                "1080p": upload_result['eager'][0].get('secure_url') or upload_result['eager'][0].get('url'),
                "720p": upload_result['eager'][1].get('secure_url') or upload_result['eager'][1].get('url'),
                "480p": upload_result['eager'][2].get('secure_url') or upload_result['eager'][2].get('url'),
            },
            "thumbnail": thumb_url
        }
        collection.insert_one(result)
        return result

    

class VideoViewSet(BaseModelViewSet):
    client = pymongo.MongoClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DATABASE]
    collection = db[settings.MONGODB_COLLECTION]
    queryset = list(collection.find())
    serializer_class = VideoSerializer

    
