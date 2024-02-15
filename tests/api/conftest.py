import sys
from pathlib import Path

import pytest

here = Path(__file__).parent
sys.path.insert(0, str(here / "../src"))
sys.path.insert(0, str(here / "extras"))


@pytest.fixture(autouse=True)
def api_setup(db):
    from testutils.utils import set_flag

    set_flag("MENU_API", True).start()
