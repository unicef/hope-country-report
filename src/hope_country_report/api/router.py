from rest_framework.routers import DefaultRouter
from rest_framework_extensions.routers import NestedRouterMixin

from . import views


class SimpleRouterWithNesting(NestedRouterMixin, DefaultRouter):
    pass


router = SimpleRouterWithNesting()
router.register("home", views.HCRHomeViewSet, basename="home")


office = router.register(r"offices", views.CountryOfficeViewSet)
q = office.register(r"queries", views.QueryViewSet, basename="queries", parents_query_lookups=["country_office__slug"])
d = q.register(
    r"dataset", views.DatasetViewSet, basename="dataset", parents_query_lookups=["country_office__slug", "query"]
)

report = office.register(
    r"config", views.ReportViewSet, basename="config", parents_query_lookups=["country_office__slug"]
)
report.register(
    r"documents",
    views.DocumentViewSet,
    basename="document",
    parents_query_lookups=["report__country_office__slug", "report__id"],
)


router.register(r"queries", views.QueryViewSet)
router.register(r"charts", views.ChartViewSet)
#
# office_router = routers.ExtendedSimpleRouter()
#
# office_router.register(r'tasks', TaskViewSet)
#           .register(r'comments',
#                     CommentViewSet,
#                     'tasks-comment',
#                     parents_query_lookups=['object_id'])
