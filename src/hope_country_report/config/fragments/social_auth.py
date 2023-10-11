from ..settings import env  # type: ignore[attr-defined]

KEY = SOCIAL_AUTH_KEY = env("AZURE_B2C_CLIENT_ID", default=None)
SOCIAL_AUTH_SECRET = env("AZURE_B2C_CLIENT_SECRET", default=None)
SOCIAL_AUTH_TENANT_NAME = env("TENANT_NAME", default="unicefpartners")
SOCIAL_AUTH_TENANT_ID = f"{SOCIAL_AUTH_TENANT_NAME}.onmicrosoft.com"
SOCIAL_AUTH_TENANT_B2C_URL = f"{SOCIAL_AUTH_TENANT_NAME}.b2clogin.com"

SOCIAL_AUTH_URL_NAMESPACE = "social"
SOCIAL_AUTH_SANITIZE_REDIRECTS = False
SOCIAL_AUTH_JSONFIELD_ENABLED = True
# SOCIAL_AUTH_POLICY = env("AZURE_B2C_POLICY_NAME", default="B2C_1_UNICEF_SOCIAL_signup_signin")
SOCIAL_AUTH_USER_MODEL = "core.User"

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

USER_FIELDS = ["username", "email", "first_name", "last_name"]
USERNAME_IS_FULL_EMAIL = True

SOCIAL_AUTH_JWT_LEEWAY = env.int("JWT_LEEWAY", 0)
