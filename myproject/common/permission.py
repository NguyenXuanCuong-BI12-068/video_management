from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from users.models import Role


def has_permission(required_permission):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):
            user = request.user

            if not user.is_authenticated:
                try:
                    guest_role = Role.objects.get(name="guest")
                    role_permissions = guest_role.permissions
                except Role.DoesNotExist:
                    role_permissions = []
            else:
                role = getattr(user, "role", None)
                role_permissions = role.permissions if role else []

            if required_permission not in role_permissions:
                return Response(
                    {"detail": "You do not have permission to perform this action."},
                    status=status.HTTP_403_FORBIDDEN
                )

            return view_func(self, request, *args, **kwargs)

        return _wrapped_view
    return decorator