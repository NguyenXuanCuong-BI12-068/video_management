from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from enum import Enum

class PermissionEnum(str, Enum):
    UPLOAD_VIDEO = "upload_video"
    DELETE_VIDEO = "delete_video"
    MANAGE_USERS = "manage_users"
    WATCH_VIDEO = "watch_video"
    COMMENT = "comment"
    LIKE = "like"
# -------------------------------
# Role Model
# -------------------------------
def validate_permissions(value):
    invalid = [v for v in value if v not in PermissionEnum._value2member_map_]
    if invalid:
        raise ValidationError(f"Invalid permissions: {invalid}")

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)   # Admin, User, Guest
    permissions = models.JSONField(default=list, blank=True, validators=[validate_permissions])  # List Enum values

    def __str__(self):
        return self.name


# -------------------------------
# User Manager (quản lý user)
# -------------------------------
class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field is required")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)

        if not user.role:
            try:
                default_role = Role.objects.get(name="user")
            except Role.DoesNotExist:
                default_role = None
            user.role = default_role

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)


# -------------------------------
# User Model
# -------------------------------
class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, related_name="users")
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    # Django required fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.username


# -------------------------------
# Activity Log
# -------------------------------
class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ("LOGIN", "Login"),
        ("LOGOUT", "Logout"),
        ("UPLOAD_VIDEO", "Upload video"),
        ("WATCH_VIDEO", "Watch video"),
        ("UPDATE_PROFILE", "Update profile"),
        ("CHANGE_PASSWORD", "Change password"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activity_logs")
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.action} at {self.timestamp}"

