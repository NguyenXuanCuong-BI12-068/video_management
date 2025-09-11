from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from .models import Role
from common.utils import *

class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        user.role = Role.objects.get(name="user")
        user.save()
        log_activity(user, "LOGIN")
        return user
    