from unicef_security.models import AbstractUser


class User(AbstractUser):
    class Meta:
        app_label = "core"
