from users.models import Role, User
from .utils import PermissionEnum

def init_db():
    try:
        if not Role.objects.all().exists():
            list_role = [
                Role(name="admin", permissions=[PermissionEnum.UPLOAD_VIDEO.value, PermissionEnum.DELETE_VIDEO.value, PermissionEnum.MANAGE_USERS.value, PermissionEnum.WATCH_VIDEO.value, PermissionEnum.COMMENT.value, PermissionEnum.LIKE.value]),
                Role(name="user", permissions=[PermissionEnum.UPLOAD_VIDEO.value, PermissionEnum.DELETE_VIDEO.value, PermissionEnum.WATCH_VIDEO.value, PermissionEnum.COMMENT.value, PermissionEnum.LIKE.value]),
                Role(name="guest", permissions=[PermissionEnum.WATCH_VIDEO.value]),
            ]
            Role.objects.bulk_create(list_role)

        if not User.objects.exists():
            admin_role = Role.objects.get(name="admin")
            admin = User.objects.create(
                email="admin@gmail.com",
                username="admin",
                password="admin",
                role=admin_role,
                is_staff=True
            )
            admin.set_password("admin")
            admin.save()
    except Exception as e:
        print(e)