from ..settings import env

TENANT_IS_MASTER = env("TENANT_IS_MASTER")
TENANT_TENANT_MODEL = "core.CountryOffice"

if TENANT_IS_MASTER:
    SESSION_COOKIE_NAME = "m_hcr_sid"
else:
    SESSION_COOKIE_NAME = "t_hcr_sid"
