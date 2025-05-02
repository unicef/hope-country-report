from typing import Callable

import pytest
from unittest import mock
from unittest.mock import Mock

from django.contrib.admin.sites import site
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.db.models.options import Options
from django.urls import reverse

from admin_extra_buttons.handlers import ChoiceHandler
from django_regex.utils import RegexList as _RegexList

from hope_country_report.apps.power_query.models import ReportConfiguration

pytestmark = [pytest.mark.admin, pytest.mark.smoke, pytest.mark.django_db]


class RegexList(_RegexList):
    def extend(self, __iterable) -> None:
        for e in __iterable:
            self.append(e)


GLOBAL_EXCLUDED_MODELS = RegexList(
    [
        r"django_celery_beat\.ClockedSchedule",
        r"contenttypes\.ContentType",
        r"hope\.Individual",
        r"hope\.Household",
        r"hope\.Program",
        r"hope\.PaymentPlan",
        r"hope\.Area",
        r"hope\.AreaType",
        r"hope\.Country",
        "authtoken",
        "social_django",
        "depot",
    ]
)

GLOBAL_EXCLUDED_BUTTONS = RegexList(
    [
        "core.UserAdmin:link_user_data",
        "core.UserAdmin:ad",
        "power_query.QueryAdmin:run",
    ]
)

KWARGS = {}


def log_submit_error(res):
    try:
        return f"Submit failed with: {repr(res.context['form'].errors)}"
    except KeyError:
        return "Submit failed"


def pytest_generate_tests(metafunc):
    import django

    markers = metafunc.definition.own_markers
    excluded_models = RegexList(GLOBAL_EXCLUDED_MODELS)
    excluded_buttons = RegexList(GLOBAL_EXCLUDED_BUTTONS)

    if "skip_models" in [m.name for m in markers]:
        skip_rule = list(filter(lambda m: m.name == "skip_models", markers))[0]
        excluded_models.extend(skip_rule.args)
    if "skip_buttons" in [m.name for m in markers]:
        skip_rule = list(filter(lambda m: m.name == "skip_buttons", markers))[0]
        excluded_buttons.extend(skip_rule.args)

    django.setup()

    if "button_handler" in metafunc.fixturenames:
        m = []
        ids = []
        for model, admin in site._registry.items():
            admin_class_name = admin.__class__.__name__

            if hasattr(admin, "get_changelist_buttons"):
                name = model._meta.object_name
                assert admin.urls
                buttons = admin.extra_button_handlers.values()
                full_name = f"{model._meta.app_label}.{name}"
                admin_name = f"{model._meta.app_label}.{admin.__class__.__name__}"
                if full_name not in excluded_models:
                    for btn in buttons:
                        tid = f"{admin_name}:{btn.name}"
                        if tid not in excluded_buttons:
                            m.append([admin, btn])
                            ids.append(tid)
        metafunc.parametrize("modeladmin,button_handler", m, ids=ids)
    elif "modeladmin" in metafunc.fixturenames:
        m = []
        ids = []
        for model, admin in site._registry.items():
            admin_class_name = admin.__class__.__name__

            name = model._meta.object_name
            full_name = f"{model._meta.app_label}.{name}"
            if full_name not in excluded_models:
                m.append(admin)
                ids.append(f"{admin_class_name}:{full_name}")
        metafunc.parametrize("modeladmin", m, ids=ids)


@pytest.fixture()
def record(db, request):
    from testutils.factories import get_factory_for_model

    modeladmin = request.getfixturevalue("modeladmin")
    instance = modeladmin.model.objects.first()
    if not instance:
        full_name = f"{modeladmin.model._meta.app_label}.{modeladmin.model._meta.object_name}"
        factory = get_factory_for_model(modeladmin.model)
        try:
            instance = factory(**KWARGS.get(full_name, {}))
        except Exception as e:
            raise Exception(f"Error creating fixture using {factory}") from e
    return instance


@pytest.fixture()
def report_config(db, afghanistan):
    from testutils.factories import ReportConfigurationFactory

    return ReportConfigurationFactory(country_office=afghanistan)


@pytest.fixture()
def app(django_app_factory, mocked_responses, monkeypatch):
    from testutils.factories import SuperUserFactory

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


def test_admin_index(app):
    url = reverse("admin:index")

    res = app.get(url)
    assert res.status_code == 200


@pytest.mark.skip_models(
    "constance.Config",
)
def test_admin_changelist(app, modeladmin, record):
    url = reverse(admin_urlname(modeladmin.model._meta, "changelist"))
    opts: Options = modeladmin.model._meta
    res = app.get(url)
    assert res.status_code == 200, res.location
    assert str(opts.app_config.verbose_name) in str(res.content)
    if modeladmin.has_change_permission(Mock(user=app._user)):
        assert f"/{record.pk}/change/" in res.body.decode()


def show_error(res):
    errors = []
    for k, v in dict(res.context["adminform"].form.errors).items():
        errors.append(f"{k}: {''.join(v)}")
    return (f"Form submitting failed: {res.status_code}: {errors}",)


@pytest.mark.skip_models(
    "constance.Config",
    "hope",
    "advanced_filters.AdvancedFilter",
)
def test_admin_changeform(app, modeladmin, record):
    opts: Options = modeladmin.model._meta
    url = reverse(admin_urlname(opts, "change"), args=[record.pk])

    res = app.get(url)
    assert str(opts.app_config.verbose_name) in res.body.decode()
    if modeladmin.has_change_permission(Mock(user=app._user)):
        res = res.forms[1].submit()
        assert res.status_code in [302, 200]


@pytest.mark.skip_models(
    "constance.Config",
    "djstripe.WebhookEndpoint",
    "advanced_filters.AdvancedFilter",
)
def test_admin_add(app, modeladmin):
    url = reverse(admin_urlname(modeladmin.model._meta, "add"))
    if modeladmin.has_add_permission(Mock(user=app._user)):
        res = app.get(url)
        res = res.forms[1].submit()
        assert res.status_code in [200, 302], log_submit_error(res)
    else:
        pytest.skip("No 'add' permission")


@pytest.mark.skip_models(
    "constance.Config",
    "hope",
)
def test_admin_delete(app, modeladmin, record, monkeypatch):
    url = reverse(admin_urlname(modeladmin.model._meta, "delete"), args=[record.pk])
    if modeladmin.has_delete_permission(Mock(user=app._user)):
        res = app.get(url)
        res.forms[1].submit()
        assert res.status_code in [200, 302]
    else:
        pytest.skip("No 'delete' permission")


def test_reportconfig_admin_inspect(app, report_config):
    """Test the celery inspect view."""
    with mock.patch.object(ReportConfiguration, "curr_async_result_id", "some-task-id", create=True):
        url = reverse("admin:power_query_reportconfiguration_celery_inspect", args=[report_config.pk])
        res = app.get(url)
        assert res.status_code == 200


def test_reportconfig_admin_queue(app, report_config):
    """Test the celery queue action."""
    url = reverse("admin:power_query_reportconfiguration_celery_queue", args=[report_config.pk])

    with mock.patch.object(ReportConfiguration, "queue") as mock_queue:
        res = app.get(url)
        assert res.status_code == 200
        assert f"Confirm queue action for {report_config}" in res.text

        res_post = res.forms[1].submit()
        assert res_post.status_code == 302
        expected_redirect_url = reverse("admin:power_query_reportconfiguration_change", args=[report_config.pk])
        assert res_post.url == expected_redirect_url
        mock_queue.assert_called_once()

    res_follow = res_post.follow()
    assert res_follow.status_code == 200
    messages = [m.message for m in res_follow.context["messages"]]
    assert "Queued" in messages[0]

    with mock.patch.object(ReportConfiguration, "is_queued", return_value=True):
        change_url = reverse("admin:power_query_reportconfiguration_change", args=[report_config.pk])
        res_get_again = app.get(url, headers={"Referer": change_url})
        assert res_get_again.status_code == 302
        assert res_get_again.location == change_url
        res_follow_again = res_get_again.follow()
        assert res_follow_again.status_code == 200
        messages = [m.message for m in res_follow_again.context["messages"]]
        assert "Task has already been queued." in messages[0]


def test_reportconfig_admin_terminate(app, report_config):
    """Test the celery terminate action."""
    url = reverse("admin:power_query_reportconfiguration_celery_terminate", args=[report_config.pk])

    change_url = reverse("admin:power_query_reportconfiguration_change", args=[report_config.pk])
    with mock.patch.object(ReportConfiguration, "is_queued", return_value=False):
        res_get = app.get(url, headers={"Referer": change_url})
        assert res_get.status_code == 302, "Expected a redirect when task is not queued"
        assert res_get.location == change_url, "Redirect should go to the change page"
        res_follow = res_get.follow()
        messages = [m.message for m in res_follow.context["messages"]]
        assert "Task not queued." in messages

    with mock.patch.object(ReportConfiguration, "is_queued", return_value=True):
        with mock.patch.object(ReportConfiguration, "terminate") as mock_terminate:
            res = app.get(url)
            assert res.status_code == 200
            assert f"Confirm termination request for {report_config}" in res.text

            change_url = reverse("admin:power_query_reportconfiguration_change", args=[report_config.pk])

            res_post = res.forms[1].submit()
            assert res_post.status_code == 302
            assert res_post.location == change_url, "Redirect should go back to the change page"
            mock_terminate.assert_called_once()

            res_follow = res_post.follow()
            messages = [m.message for m in res_follow.context["messages"]]
            assert len(messages) > 0, "Expected success/info message after terminate"


def test_reportconfig_admin_revoke(app: Callable, report_config: ReportConfiguration) -> None:
    """Test the celery revoke action."""
    url = reverse("admin:power_query_reportconfiguration_celery_revoke", args=[report_config.pk])

    change_url = reverse("admin:power_query_reportconfiguration_change", args=[report_config.pk])
    with mock.patch.object(ReportConfiguration, "is_queued", return_value=False):
        res_get = app.get(url, headers={"Referer": change_url})
        assert res_get.status_code == 302, "Expected a redirect when task is not queued"
        assert res_get.location == change_url, "Redirect should go to the change page"
        res_follow = res_get.follow()
        messages = [m.message for m in res_follow.context["messages"]]
        assert "Task not queued." in messages

    with mock.patch.object(ReportConfiguration, "is_queued", return_value=True):
        with mock.patch.object(ReportConfiguration, "revoke") as mock_revoke:
            res = app.get(url)
            assert res.status_code == 200
            assert f"Confirm revoking action for {report_config}" in res.text

            change_url = reverse("admin:power_query_reportconfiguration_change", args=[report_config.pk])
            res_post = res.forms[1].submit()
            assert res_post.status_code == 302
            assert res_post.location == change_url, "Redirect should go back to the change page"
            mock_revoke.assert_called_once()

            res_follow = res_post.follow()
            messages = [m.message for m in res_follow.context["messages"]]
            assert "Revoked" in messages


@pytest.mark.skip_buttons()
def test_admin_buttons(app, modeladmin, button_handler, record, monkeypatch):
    from admin_extra_buttons.handlers import LinkHandler

    if isinstance(button_handler, ChoiceHandler):
        pass
    elif isinstance(button_handler, LinkHandler):
        btn = button_handler.get_button({"original": record})
        button_handler.func(None, btn)
    else:
        if len(button_handler.sig.parameters) == 2:
            url = reverse(f"admin:{button_handler.url_name}")
        else:
            url = reverse(f"admin:{button_handler.url_name}", args=[record.pk])

        res = app.get(url)
        assert res.status_code in [200, 302]
