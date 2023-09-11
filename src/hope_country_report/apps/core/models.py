from unicef_security.models import AbstractUser


class User(AbstractUser):  # type: ignore
    class Meta:
        app_label = "core"
