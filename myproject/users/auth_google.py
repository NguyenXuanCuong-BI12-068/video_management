from google.oauth2 import id_token
from google.auth.transport.requests import Request
from django.http import JsonResponse
import requests
from django.conf import settings
from rest_framework import status
from django.utils.timezone import now as djnow
from common.utils import *
from users.models import User, Role
def login_sso(request):
    code = request.GET.get("code")
    if not code:
        return JsonResponse({"detail": "Missing code"}, status=400)

    token_resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
    )
    token_data = token_resp.json()
    token = token_data.get('id_token')
    try:
        idinfo = id_token.verify_oauth2_token(token, Request(), settings.GOOGLE_OAUTH2_CLIENT_ID)
        email = idinfo.get('email')
        name = idinfo.get('name')
        picture = idinfo.get('picture')
        if not email:
            return JsonResponse({"detail": "Email required."}, status=400)
        user, created = User.objects.get_or_create(
            email=email, defaults={"username": name, "avatar": picture, "role": Role.objects.get(name="user")}
        )
        if not created:
            user.role = Role.objects.get(name="user")
            user.save(update_fields=["role"])
        user.last_login = djnow()
        user.save(update_fields=["last_login"])
        log_activity(user, "LOGIN")
        return JsonResponse({
            'detail': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role.name if user.role else None,
            }
        }, status=200)
    except ValueError:
        return JsonResponse({"detail": "Token invalid"}, status=400)