import contextlib
import re
from urllib.parse import urlsplit, urlunsplit

from django.contrib.admin.utils import unquote
from django.core.signing import get_cookie_signer
from django.urls import NoReverseMatch, resolve, Resolver404, reverse
from django.utils.regex_helper import _lazy_re_compile
from django.utils.translation.trans_real import language_code_prefix_re

from tenant_admin.config import conf

tenant_code_re = _lazy_re_compile(r"^[0-9A-Z]{4}$", re.IGNORECASE)

tenant_code_prefix_re = _lazy_re_compile(r"^/([0-9A-Z]{4})(/|$)")


def get_tenant_from_path(path, strict=False):
    """
    Return the language code if there's a valid language code found in `path`.

    If `strict` is False (the default), look for a country-specific variant
    when neither the language code nor its generic variant is found.
    """
    regex_match = tenant_code_prefix_re.match(path)
    if not regex_match:
        return None
    lang_code = regex_match[1]
    return lang_code


def get_tenant_from_request(request):
    signer = get_cookie_signer()
    cookie_value = request.COOKIES.get(conf.COOKIE_NAME)
    if cookie_value:
        return signer.unsign(cookie_value)


@contextlib.contextmanager
def override(tenant_pk):
    from hope_country_report.apps.core.models import CountryOffice

    conf.strategy.set_selected_tenant(CountryOffice.objects.get(pk=tenant_pk))
    yield


def tenantize_url(url, tenant):
    """
    Given a URL (absolute or relative), try to get its translated version in
    the `lang_code` language (either by i18n_patterns or by translated regex).
    Return the original URL if no translated version is found.
    """
    parsed = urlsplit(url)
    try:
        # URL may be encoded.
        match = resolve(unquote(parsed.path))
    except Resolver404:
        pass
    else:
        to_be_reversed = "%s:%s" % (match.namespace, match.url_name) if match.namespace else match.url_name
        try:
            url = reverse(to_be_reversed, args=match.args, kwargs=match.kwargs)
            url = f"/{tenant}{url}"
        except NoReverseMatch:
            pass
        else:
            url = urlunsplit((parsed.scheme, parsed.netloc, url, parsed.query, parsed.fragment))
    print("src/tenant_admin/utils.py: 44", 111111, tenant, url)
    return url
