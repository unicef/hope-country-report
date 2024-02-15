import json
import re
from contextlib import ContextDecorator
from pathlib import Path
from urllib.parse import parse_qs

from django.http import QueryDict
from django.urls import reverse

import responses


class MutableQueryDict(QueryDict):
    def __init__(self, query_string=None, mutable=False, encoding=None):
        super().__init__(query_string, mutable, encoding)
        self._mutable = True

    def unflat(self: QueryDict) -> dict:
        # Transform `{'attributes[]': 'size', 'attributes[]': 'gender'}` into
        # `{'attributes': ['size', 'gender']}`
        def handle_multiple_keys(multidict: QueryDict):
            data = dict()
            for k in multidict.keys():
                values = multidict.getlist(k)
                values = [handle_multiple_keys(v) if hasattr(v, "keys") else v for v in values]
                if len(k) > 2 and k.endswith("[]"):
                    k = k[:-2]
                else:
                    values = values[0]
                data[k] = values
            return data

        data = handle_multiple_keys(self)

        def make_tree(data):
            for k, v in list(data.items()):
                r = re.search(r"^([^\[]+)\[([^\[]+)\](.*)$", k)
                if r:
                    k0 = r.group(1)
                    k1 = r.group(2) + r.group(3)
                    data[k0] = data.get(k0, {})
                    data[k0][k1] = v
                    data[k0] = make_tree(data[k0])
                    del data[k]
            return data

        data = make_tree(data)

        # Transform `{'items': {'0': {'plan': 'pro-yearly'}}}` into
        # `{'items': [{'plan': 'pro-yearly'}]}`
        def transform_lists(data):
            if len(data) > 0 and all([re.match(r"^[0-9]+$", k) for k in data.keys()]):
                new_data = [(int(k), v) for k, v in data.items()]
                new_data.sort(key=lambda k: int(k[0]))
                data = []
                for k, v in sorted(new_data, key=lambda k: int(k[0])):
                    if type(v) is dict:
                        data.append(transform_lists(v))
                    else:
                        data.append(v)
                return data
            else:
                for k in data.keys():
                    if type(data[k]) is dict:
                        data[k] = transform_lists(data[k])
                return data

        data = transform_lists(data)

        return data


def payload(filename, section=None, merge: dict | None = None):
    data = json.load((Path(__file__).parent / filename).open())
    if section:
        return data[section]
    if merge:
        data = {**data, **merge}
    return data


def check_link_by_class(selenium, cls, view_name):
    link = selenium.find_element_by_class_name(cls)
    url = reverse(f"{view_name}")
    return f' href="{url}"' in link.get_attribute("innerHTML")


def get_all_attributes(driver, element):
    return list(
        driver.execute_script(
            "var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) {"
            " items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value"
            " }; return items;",
            element,
        )
    )


def mykey(group, request):
    return request.META["REMOTE_ADDR"][::-1]


def callable_rate(group, request):
    if request.user.is_authenticated:
        return None
    return (0, 1)


def matcher_address(address):
    def match(request):
        try:
            request_body = request.body.decode("utf-8")
            return address == json.loads(request_body)["address"], ""
        except responses.JSONDecodeError:
            return False
        except KeyError:
            return False

    return match


def matcher_debugger(return_value=True):
    def debugger(request_body):
        try:
            if isinstance(request_body, bytes):
                request_body = request_body.decode("utf-8")
            try:
                payload = json.loads(request_body)
            except responses.JSONDecodeError:
                try:
                    payload = parse_qs(request_body)
                except Exception:
                    payload = request_body
        except Exception:
            pass
        print("##### MATCHER_DEBUGGER", payload, return_value)
        return return_value

    return debugger


class set_flag(ContextDecorator):  # noqa
    def __init__(self, flag_name: str, on_off: bool):
        self.flag_name = flag_name
        self.on_off = on_off
        self.old_state = None

    def __enter__(self):
        from flags.state import _set_flag_state, flag_state

        self.old_state = flag_state(self.flag_name)
        _set_flag_state(self.flag_name, self.on_off)

        return self

    def __exit__(self, e_typ, e_val, trcbak):
        from flags.state import _set_flag_state

        _set_flag_state(self.flag_name, self.old_state)

        if e_typ:
            raise e_val.with_traceback(trcbak)

    def start(self):
        """Activate a patch, returning any created mock."""
        result = self.__enter__()
        return result

    def stop(self):
        """Stop an active patch."""
        return self.__exit__(None, None, None)


def get_messages(res):
    if hasattr(res, "context") and "messages" in res.context:
        return list(map(str, res.context["messages"]))
    return []


def assert_submit(res, name="form", code: int = 302):
    assert res.status_code == code, f"Expected {code} got {res.status_code}"
    assert not res.context[name].errors, res.context[name].errors


def assert_fail(res, name="form", code: int = 200):
    assert res.status_code == code, f"Expected {code} got {res.status_code}"
    assert res.context[name].errors, res.context[name].errors
