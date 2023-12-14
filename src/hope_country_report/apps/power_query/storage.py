from django.core.files.storage import FileSystemStorage
from storages.backends.azure_storage import AzureStorage
from django.conf import settings


class DataSetStorage(FileSystemStorage):
    def get_available_name(self, name: str, max_length: int | None = None) -> str:
        if self.exists(name):
            self.delete(name)
        return name


class HCRAzureStorage(AzureStorage):
    prefix = ""

    def get_default_settings(self):
        base = {**self.get_default_settings()}
        for k, v in base.items():
            if hasattr(settings, f"{self.prefix}_{k.upper()}"):
                base[k] = getattr(f"{self.prefix}_{k.upper()}")
        return base


class HopeStorage(HCRAzureStorage):
    prefix = "HOPE"


class MediaStorage(HCRAzureStorage):
    prefix = "MEDIA"
