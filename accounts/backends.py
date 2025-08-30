from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailOrUsernameBackend(ModelBackend):
    """
    E-Mail-ONLY Login: Wir interpretieren das 'username'-Feld der Login-Form als E-Mail.
    (Wenn du auch Username erlauben willst, erweitere die Logik.)
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        email = (username or "").strip()
        if not email or not password:
            return None
        User = get_user_model()
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
