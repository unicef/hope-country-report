from django.contrib import admin

from unicef_security.admin import UserAdminPlus as _UserAdminPlus

from hope_country_report.apps.core.models import User


@admin.register(User)
class UserAdminPlus(_UserAdminPlus):  # type: ignore
    pass
