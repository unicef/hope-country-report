import pytest
from django.conf import settings
from django.contrib.sessions.models import Session
from django.test import Client
from django.urls import reverse

pytestmark = [pytest.mark.django_db]


def test_unicef_logout_invalidates_session(user):
    """unicef-security must flush the Django session server-side on logout.

    Regression test for the WAPT finding "Session does not get invalidated at
    logout": the token captured before logout must no longer be accepted.
    """
    client = Client()
    client.force_login(user)
    session_key = client.session.session_key
    assert Session.objects.filter(session_key=session_key).exists()

    res = client.get(reverse("security:unicef-logout"))
    assert res.status_code in (200, 302)

    # server-side session is gone
    assert not Session.objects.filter(session_key=session_key).exists()

    # a client replaying the captured cookie is no longer authenticated
    replay = Client()
    replay.cookies[settings.SESSION_COOKIE_NAME] = session_key
    res = replay.get("/", follow=False)
    assert res.status_code == 302
    assert "/login/" in res["Location"]
