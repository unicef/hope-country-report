from typing import List, Tuple, TypeVar, Union

from hope_country_report.apps.power_query.models._base import PowerQueryModel

DocumentResult = tuple[int, Union[str, int]]
ReportDocumentResult = Tuple[int | None, Exception | str]

ReportResult = List[str | ReportDocumentResult]

QueryMatrixResult = dict[str, Union[int, str]]
_PowerQueryModel = TypeVar("_PowerQueryModel", bound=PowerQueryModel, covariant=True)
