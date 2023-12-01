from ..settings import env  # type: ignore[attr-defined]

# Social Auth settings.
SOCIAL_AUTH_SECRET = env.str("AZURE_CLIENT_SECRET")
SOCIAL_AUTH_TENANT_ID = env("AZURE_TENANT_ID")
SOCIAL_AUTH_KEY = env.str("AZURE_CLIENT_KEY")

SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = [
    "username",
    "first_name",
    "last_name",
    "email",
]
SOCIAL_AUTH_JSONFIELD_ENABLED = True

SOCIAL_AUTH_PIPELINE = (
    "unicef_security.pipeline.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.user.get_username",
    "social_core.pipeline.social_auth.associate_by_email",
    "unicef_security.pipeline.create_unicef_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
)
SOCIAL_AUTH_AZUREAD_B2C_OAUTH2_USER_FIELDS = [
    "email",
    "fullname",
]

SOCIAL_AUTH_AZUREAD_B2C_OAUTH2_SCOPE = [
    "openid",
    "email",
    "profile",
]

SOCIAL_AUTH_SANITIZE_REDIRECTS = True
SOCIAL_AUTH_REDIRECT_IS_HTTPS = env.bool("SOCIAL_AUTH_REDIRECT_IS_HTTPS")

SOCIAL_LOGIN_URL = "/social/azuread-tenant-oauth2"
