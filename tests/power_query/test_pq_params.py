def test_parameter(db) -> None:
    from testutils.factories import ParametrizerFactory

    p = ParametrizerFactory()
    p.refresh()
