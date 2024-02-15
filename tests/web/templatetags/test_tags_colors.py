from hope_country_report.web.templatetags.colors import color, random_color


def test_color():
    assert color("abc") == color("abc")
    assert color("abc") != color("abcabcabcabc")


def test_randomcolor():
    assert [random_color(), random_color(), random_color()] == ["blue", "red", "gray"]
