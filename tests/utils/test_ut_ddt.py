from unittest.mock import MagicMock, Mock

from hope_country_report.utils.ddt import StateDebugPanel


def test_ddt_panel():
    # newver raise exceptio here
    panel = StateDebugPanel(Mock(), MagicMock())
    assert panel.nav_title()
    assert panel.title()
    assert panel.content
