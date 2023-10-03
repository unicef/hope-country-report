from django import forms
from django.contrib.admin.forms import AdminAuthenticationForm
from django.core.exceptions import ValidationError

from .config import conf


class TenantAuthenticationForm(AdminAuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError(
                self.error_messages["inactive"],
                code="inactive",
            )


class SelectTenantForm(forms.Form):
    tenant = forms.ModelChoiceField(queryset=None)
    next = forms.CharField(required=False)

    def __init__(self, *args, **kwargs) -> None:
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        self.fields["tenant"].queryset = conf.auth.get_allowed_tenants(self.request)
