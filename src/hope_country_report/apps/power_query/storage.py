import os

from django.core.files.storage import FileSystemStorage

from storages.backends.azure_storage import AzureStorage


class DataSetStorage(FileSystemStorage):
    def get_available_name(self, name: str, max_length: int | None = None) -> str:
        if self.exists(name):
            self.delete(name)
        return name


class HCRAzureStorage(AzureStorage):
    prefix = ""

    def get_default_settings(self):
        base = super().get_default_settings()
        for k, v in base.items():
            if value := os.getenv(f"{self.prefix}_AZURE_{k.upper()}", None):
                base[k] = value
        return base


class HopeStorage(HCRAzureStorage):
    prefix = "HOPE"


class MediaStorage(HCRAzureStorage):
    prefix = "MEDIA"

    def get_available_name(self, name: str, max_length: int | None = None) -> str:
        if self.exists(name):
            self.delete(name)
        return name


class StaticStorage(HCRAzureStorage):
    prefix = "STATIC"
