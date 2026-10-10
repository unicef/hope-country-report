from django.urls import path
from admin_extra_buttons.mixins import ExtraButtonsMixin


class StaffGatedExtraButtonsMixin(ExtraButtonsMixin):
    """Enforce the admin staff gate on admin_extra_buttons URLs.

    ``ExtraButtonsMixin.get_extra_urls()`` registers button handlers as raw
    ``path()`` entries, outside ``AdminSite.admin_view``. As a result those views
    skip ``AdminSite.has_permission`` and any authenticated user could reach them.
    Re-wrap each generated URL with ``admin_view`` so the same staff/permission
    checks that protect the rest of the admin also apply to the buttons.
    """

    def get_extra_urls(self):
        urls = []
        for url in super().get_extra_urls():
            view = self.admin_site.admin_view(url.callback)
            urls.append(path(str(url.pattern), view, name=url.name))
        return urls
