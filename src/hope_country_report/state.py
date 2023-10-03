import json
from threading import local
from time import asctime

from django.http import HttpResponse


class State(local):
    request = None
    tenant = None
    cookies = {}

    def __init__(self):
        self.timestamp = asctime()

    def __repr__(self):
        return f"<State {id(self)} - {self.timestamp}>"

    def add_cookies(
        self, key, value, max_age=None, expires=None, path="/", domain=None, secure=False, httponly=False, samesite=None
    ):
        value = json.dumps(value)
        self.cookies[key] = [value, max_age, expires, path, domain, secure, httponly, samesite]

    def set_cookies(self, response: "HttpResponse"):
        for name, args in self.cookies.items():
            response.set_cookie(name, *args)


state = State()
