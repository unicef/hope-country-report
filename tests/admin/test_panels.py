import pytest
from django.contrib.admin.sites import site

pytestmark = pytest.mark.admin


def pytest_generate_tests(metafunc):
    import django

    django.setup()
    if "panel" in metafunc.fixturenames:
        m = []
        ids = []
        for panel in site.console_panels:
            if panel["name"] not in []:
                m.append(pytest.param(panel, marks=[pytest.mark.admin]))
                ids.append(f"{panel['name']}/{panel['label']}")
        metafunc.parametrize("panel", m, ids=ids)

#
# @pytest.mark.admin
# def test_panel(panel, django_app, admin_user):
#     url = reverse(f"admin:{panel['name']}")
#     res = django_app.get(url, user=admin_user)
#     assert res.status_code == 200
#
#
# def test_panel_firebase(django_app, admin_user):
#     url = reverse("admin:firebase_panel")
#     res = django_app.get(url, user=admin_user)
#     assert res.status_code == 200
#     res = res.form.submit()
#     assert res.status_code == 200
#
#
# def test_panel_sql(django_app, admin_user):
#     url = reverse("admin:panel_sql")
#     res = django_app.get(url, user=admin_user)
#     res = res.form.submit()
#     assert res.status_code == 200
#
#     res = django_app.get(url, user=admin_user)
#     res.form["command"] = btoa(quote("SELECT * from auth_userSELECT * FROM information_schema.tables;"))
#     res = res.form.submit()
#     assert res.status_code == 200
#
#
# def test_panel_email(django_app, admin_user):
#     url = reverse("admin:email")
#     res = django_app.get(url, user=admin_user)
#     res = res.form.submit()
#     assert res.status_code == 200
#
#
# def test_panel_stripe(mocked_responses, monkeypatch, django_app, admin_user):
#     from testutils.factories import AccountFactory
#
#     from sos.stripe.views import Account
#
#     monkeypatch.setattr(Account, "get_default_account", lambda: AccountFactory())
#     url = reverse("admin:stripe_panel")
#     res = django_app.get(url, user=admin_user)
#     res = res.form.submit()
#     assert res.status_code == 200
#
#
# def test_panel_celery(monkeypatch, django_app, admin_user):
#     from celery.app.control import Inspect
#
#     monkeypatch.setattr(Inspect, "stats", lambda *_: {"CeleryWorker": {"detail": "Interesting detail"}})
#     res = django_app.get(reverse("admin:panel_celery"), user=admin_user)
#     assert res.status_code == 200
#     assert "Workers Report" in res.text
#     assert "CeleryWorker" in res.text
#     assert "Interesting detail" in res.text
#
#
# def test_panel_celery_action_buildin(monkeypatch, django_app, admin_user):
#     from celery.app.control import Inspect
#
#     monkeypatch.setattr(Inspect, "registered", lambda *_: {"CeleryWorker": ["registered_task_1", "registered_task_2"]})
#     res = django_app.get(reverse("admin:panel_celery"), user=admin_user)
#     assert "Registered tasks" in res.text
#     assert "Scheduled tasks" in res.text
#     res.form["actions"] = "registered"
#
#     res = res.form.submit()
#     assert "CeleryWorker" in res.text
#     assert "registered_task_1" in res.text
#     assert "registered_task_2" in res.text
#
#
# def test_panel_celery_action_custom(monkeypatch, django_app, admin_user):
#     from celery.app.control import Inspect
#
#     monkeypatch.setattr(
#         Inspect,
#         "active",
#         lambda *_: {
#             "CeleryWorker": [
#                 {"id": "task_id_1", "detail": "Interesting detail"},
#                 {"id": "task_id_2", "detail": "Another interesting detail"},
#             ],
#             "CeleryWorker2": [{"id": "task_id_3", "detail": "More interesting detail"}],
#         },
#     )
#     res = django_app.get(reverse("admin:panel_celery"), user=admin_user)
#     assert "Active tasks" in res.text
#     res.form["actions"] = "active_flat"
#
#     res = res.form.submit()
#     assert "CeleryWorker" not in res.text
#     assert "task_id_" in res.text
#     assert "nteresting detail" in res.text
