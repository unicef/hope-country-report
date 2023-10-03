from django.urls import reverse


def test_reverse():
    url1 = reverse("admin:hope_household_changelist")
    url2 = reverse("tenant_admin:hope_household_changelist")
    assert url1 != url2
