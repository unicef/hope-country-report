def should_profile_power_query(request):
    return request.path.startswith("/power_query/")

SILKY_PYTHON_PROFILER_FUNC = should_profile_power_query
SILKY_INTERCEPT_FUNC = should_profile_power_query

# SILKY_AUTHENTICATION = True # User must login
# SILKY_AUTHORISATION = True  # User must have permissions
# SILKY_PERMISSIONS = lambda user: user.is_superuser

#
# SILKY_MAX_REQUEST_BODY_SIZE = -1  # Silk takes anything <0 as no limit
# SILKY_MAX_RESPONSE_BODY_SIZE = 1024  # If response body>1024 bytes, ignore
# SILKY_INTERCEPT_PERCENT = 50  # log only 50% of requests
# SILKY_MAX_RECORDED_REQUESTS = 10


SILKY_META = True
