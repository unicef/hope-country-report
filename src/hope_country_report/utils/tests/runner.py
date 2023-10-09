from typing import Any

from django.db.backends.utils import truncate_name
from django.test.runner import DiscoverRunner


class UnManagedModelTestRunner(DiscoverRunner):
    def setup_test_environment(self, **kwargs: Any) -> None:
        from django.apps import apps
        from django.db import connection

        get_models = apps.get_models
        self.unmanaged_models = [m for m in get_models() if not m._meta.managed]
        for m in self.unmanaged_models:
            if m._meta.proxy:
                opts = m._meta.proxy_for_model._meta
            else:
                opts = m._meta
            db_table = ("hope_ro__{0.app_label}_{0.model_name}".format(opts)).lower()
            m._meta.managed = True
            m._meta.db_table = truncate_name(db_table, connection.ops.max_name_length())
            m._meta.db_tablespace = ""

        super(UnManagedModelTestRunner, self).setup_test_environment(**kwargs)

    def teardown_test_environment(self, **kwargs: Any) -> None:
        super(UnManagedModelTestRunner, self).teardown_test_environment(**kwargs)
        for m in self.unmanaged_models:
            m._meta.managed = False
