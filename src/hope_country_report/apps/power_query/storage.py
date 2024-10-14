import os

from storages.backends.azure_storage import AzureStorage


class ReadOnlyStorageMixin:
    def delete(self, name):
        raise RuntimeError("This storage cannot delete files")

    def save(self, name, content, max_length=None):
        raise RuntimeError("This storage cannot save files")

    def open(self, name, mode="rb"):
        if "w" in mode:
            raise RuntimeError("This storage cannot open files in write mode")
        return super().open(name, mode="rb")

    def listdir(self, path=""):
        return []


class HCRAzureStorage(AzureStorage):
    prefix = ""

    def get_default_settings(self):
        base = super().get_default_settings()
        for k, v in base.items():
            if value := os.getenv(f"{self.prefix}_AZURE_{k.upper()}", None):
                base[k] = value
        return base


class HopeStorage(ReadOnlyStorageMixin, HCRAzureStorage):
    prefix = "HOPE"


class MediaStorage(HCRAzureStorage):
    prefix = "MEDIA"

    def get_available_name(self, name: str, max_length: int | None = None) -> str:
        if self.exists(name):
            self.delete(name)
        return name


class StaticStorage(HCRAzureStorage):
    prefix = "STATIC"
