from django.conf import settings
from rest_framework import serializers
import pymongo
from datetime import datetime
from bson.objectid import ObjectId
from users.models import User
class VideoSerializer(serializers.Serializer):
    STATUS_CHOICES = (
        ('active', 'ACTIVE'),
        ('inactive', 'INACTIVE'),
    )
    PRIVACY_CHOICES = (
        ('public', 'PUBLIC'),
        ('private', 'PRIVATE'),
    )

    id = serializers.CharField(read_only=True)
    uploaderId = serializers.CharField(read_only=True)
    file = serializers.FileField(default=None)
    video_url = serializers.URLField(default=None)
    title = serializers.CharField()
    description = serializers.CharField()
    duration = serializers.FloatField(default=0.0)
    size = serializers.FloatField(default=0.0)
    resolution = serializers.CharField(default='0x0')
    status = serializers.ChoiceField(choices=STATUS_CHOICES, default='active')
    privacy = serializers.ChoiceField(choices=PRIVACY_CHOICES, default='public')
    uploadDate = serializers.DateTimeField(default=datetime.now)
    viewCount = serializers.IntegerField(default=0)
    likeCount = serializers.IntegerField(default=0)
    dislikeCount = serializers.IntegerField(default=0)
    is_deleted = serializers.BooleanField(default=False)

    def create(self, validated_data):
        client = pymongo.MongoClient(settings.MONGODB_URI)
        db = client[settings.MONGODB_DATABASE]
        collection = db[settings.MONGODB_COLLECTION]
        user_id = self.context['request'].user.id
        document = {
            'title': validated_data['title'],
            'description': validated_data['description'],
            'file': self.context['file'],
            'video_url': self.context['file'],
            'duration': self.context['duration'],
            'size': self.context['size'],
            'resolution': self.context['resolution'],
            'status': validated_data['status'],
            'privacy': validated_data['privacy'],
            'uploadDate': validated_data['uploadDate'],
            'viewCount': validated_data['viewCount'],
            'likeCount': validated_data['likeCount'],
            'dislikeCount': validated_data['dislikeCount'],
            'is_deleted': validated_data['is_deleted'],
            'uploaderId': user_id,
        }
        collection.insert_one(document)
        return document

    def update(self, instance, validated_data):
        client = pymongo.MongoClient(settings.MONGODB_URI)
        db = client[settings.MONGODB_DATABASE]
        collection = db[settings.MONGODB_COLLECTION]
        object_id = self.context.get("object_id")
        document = {
            'title': validated_data.get('title', instance.get('title')),
            'description': validated_data.get('description', instance.get('description'))
        }

        updated = collection.find_one_and_update(
            {'_id': ObjectId(object_id)},
            {'$set': document},
            return_document=True
        )
        updated["id"] = str(updated["_id"])
        return updated
