import importlib

from django.conf import settings


def get_hope_storage():
    options = settings.STORAGES["hope"]["OPTIONS"]
    package_name, klass_name = settings.STORAGES["hope"]["BACKEND"].rsplit(".", 1)
    module = importlib.import_module(package_name)
    return getattr(module, klass_name)(**options)
