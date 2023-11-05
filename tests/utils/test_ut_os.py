import os
from pathlib import Path

from hope_country_report.utils.os import pushd


def test_pushd():
    current = Path(os.curdir).absolute()
    here = Path(__file__).parent.absolute()
    with pushd(here):
        assert Path(os.curdir).absolute() == here
    assert Path(os.curdir).absolute() == current

    with pushd(""):
        assert Path(os.curdir).absolute()
