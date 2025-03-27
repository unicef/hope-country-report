from typing import TypeVar

from hope_country_report.apps.power_query.models._base import PowerQueryModel

DocumentResult = tuple[int, str | int]
ReportDocumentResult = tuple[int | None, Exception | str]

ReportResult = list[str | ReportDocumentResult]

QueryMatrixResult = dict[str, int | str]
_PowerQueryModel = TypeVar("_PowerQueryModel", bound=PowerQueryModel, covariant=True)
