from hope_country_report.utils.perf import profile


def test_profile():
    with profile() as m:
        pass
    assert isinstance(m, dict)
