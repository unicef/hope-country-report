from typing import List, TypeVar, Union

from hope_country_report.apps.power_query.models import Dataset
from hope_country_report.apps.power_query.models._base import PowerQueryModel

DocumentResult = tuple[int, Union[str, int]]
ReportResult = List[List[int | None, Exception | None]]
QueryResult = tuple[Dataset, dict]
QueryMatrixResult = dict[str, Union[int, str]]
_PowerQueryModel = TypeVar("_PowerQueryModel", bound=PowerQueryModel, covariant=True)
