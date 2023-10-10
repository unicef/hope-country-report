from typing import Any

from django.test.runner import DiscoverRunner


class UnManagedModelTestRunner(DiscoverRunner):
    def setup_test_environment(self, **kwargs: Any) -> None:
        from django.apps import apps

        get_models = apps.get_models
        self.unmanaged_models = [m for m in get_models() if not m._meta.managed]
        for m in self.unmanaged_models:
            m._meta.managed = True

        super().setup_test_environment(**kwargs)

    def teardown_test_environment(self, **kwargs: Any) -> None:
        super().teardown_test_environment(**kwargs)
        for m in self.unmanaged_models:
            m._meta.managed = False
