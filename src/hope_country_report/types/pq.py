from typing import Any, Dict, List, Tuple, TypeVar, Union

from hope_country_report.apps.power_query.models import Dataset, PowerQueryModel

DocumentResult = Tuple[int, Union[str, int]]
ReportResult = List[Union[DocumentResult, Any, str]]
QueryResult = Tuple[Dataset, Dict]
QueryMatrixResult = Dict[str, Union[int, str]]
_PowerQueryModel = TypeVar("_PowerQueryModel", bound=PowerQueryModel, covariant=True)
