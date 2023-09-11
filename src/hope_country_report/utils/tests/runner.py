from typing import Any

from django.test.runner import DiscoverRunner


class UnManagedModelTestRunner(DiscoverRunner):
    def setup_test_environment(self, *args: Any, **kwargs: Any) -> None:
        from django.apps import apps

        get_models = apps.get_models
        self.unmanaged_models = [m for m in get_models() if not m._meta.managed]
        for m in self.unmanaged_models:
            m._meta.managed = True
        super(UnManagedModelTestRunner, self).setup_test_environment(*args, **kwargs)

    def teardown_test_environment(self, *args: Any, **kwargs: Any) -> None:
        super(UnManagedModelTestRunner, self).teardown_test_environment(*args, **kwargs)
        for m in self.unmanaged_models:
            m._meta.managed = False
