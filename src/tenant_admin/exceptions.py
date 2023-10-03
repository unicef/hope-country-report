class TenantAdminError(Exception):
    pass


class InvalidTenantError(TenantAdminError):
    pass


class TenantNotAuthorisedError(TenantAdminError):
    pass
