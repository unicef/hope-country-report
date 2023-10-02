#  :copyright: Copyright (c) 2018-2020. OS4D Ltd - All Rights Reserved
#  :license: Commercial
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Written by Stefano Apostolico <s.apostolico@gmail.com>, November 2020
import logging
import sys

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

from social_core.exceptions import AuthAlreadyAssociated
from sos.exceptions import SocialRegistrationError

logger = logging.getLogger(__name__)


class SocialRegistrationExceptionMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        logger.exception(exception, exc_info=sys.exc_info())
        if isinstance(exception, AuthAlreadyAssociated):
            return HttpResponseRedirect(reverse("logout"))
        elif isinstance(exception, SocialRegistrationError):
            try:
                exception.user.delete()
            except Exception:
                pass
