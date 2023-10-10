# @classmethod
# def setUpTestData(cls) -> None:
#     cls.superuser = UserFactory(is_superuser=True, is_staff=True, is_active=True)
#     cls.user1 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
#     cls.user2 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
#     create_defaults()
#     cls.query1: Query = QueryFactory(name="Query1", code="result=conn.all()")
#     cls.query2: Query = QueryFactory(
#         name="Query2", code=f"result=invoke({cls.query1.pk}, arguments)"
#     )
#     cls.formatter: Formatter = FormatterFactory(name="Queryset To HTML")
#     cls.report: Report = ReportFactory(formatter=cls.formatter, query=cls.query1)
#
# def test_query_execution(self) -> None:
#     result = self.query1.execute_matrix()
#     self.assertTrue(self.query1.datasets.exists())
#     self.assertEqual(result["{}"], self.query1.datasets.first().pk)
#
# def test_query_lazy_execution(self) -> None:
#     self.query1.execute_matrix()
#     ds1 = self.query1.datasets.first()
#     ds2, __ = self.query1.run(use_existing=True)
#     self.assertEqual(ds1.pk, ds2.pk)
#
# def test_report_execution(self) -> None:
#     self.query1.execute_matrix()
#     dataset = self.query1.datasets.first()
#     self.report.execute()
#     self.assertTrue(self.report.documents.filter(dataset=dataset).exists())
#
# def test_nested_query(self) -> None:
#     result = self.query2.execute_matrix()
#     self.assertTrue(self.query2.datasets.exists())
#     self.assertEqual(result["{}"], self.query2.datasets.first().pk)
