from contextlib import contextmanager

from tenant_admin import state


@contextmanager
def set_current_tenant(tenant):
    state.tenant = tenant
    yield
    state.tenant = None
