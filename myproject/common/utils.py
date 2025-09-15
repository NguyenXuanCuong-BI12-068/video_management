from enum import Enum
from django.core.exceptions import ValidationError

class PermissionEnum(str, Enum):
    UPLOAD_VIDEO = "upload_video"
    DELETE_VIDEO = "delete_video"
    MANAGE_USERS = "manage_users"
    WATCH_VIDEO = "watch_video"
    COMMENT = "comment"
    LIKE = "like"


def validate_permissions(value):
    invalid = [v for v in value if v not in PermissionEnum._value2member_map_]
    if invalid:
        raise ValidationError(f"Invalid permissions: {invalid}")