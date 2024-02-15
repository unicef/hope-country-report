import os
from pathlib import Path
from wsgiref.util import FileWrapper

from django.conf import settings
from django.core.files.storage import default_storage, Storage
from django.http import Http404, HttpResponse, StreamingHttpResponse

THttpResponse = type[StreamingHttpResponse | HttpResponse]


def resource_path(path: str) -> Path:
    return Path(settings.PACKAGE_DIR) / path


def download_media(
    path: str, storage: Storage | None = None, response_class: THttpResponse = StreamingHttpResponse
) -> HttpResponse | StreamingHttpResponse:
    if storage is None:
        storage = default_storage

    file_path = storage.path(path)
    chunk_size = 8192
    if storage.exists(file_path):
        response = response_class(
            FileWrapper(open(file_path, "rb"), chunk_size), content_type="application/force-download"
        )
        response["Content-Disposition"] = "inline; filename=" + os.path.basename(file_path)
        return response
    raise Http404(file_path)
