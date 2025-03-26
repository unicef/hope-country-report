#!/usr/bin/env python
import os
import sys

SRC = os.path.abspath("src")
sys.path.insert(0, SRC)
if sys.argv[1] == "test":
    os.chdir(os.path.join(SRC, "hope_country_report"))

if __name__ == "__main__":
    from hope_country_report.state import state

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hope_country_report.config.settings")
    if "inspect_hope" in sys.argv:
        state.inspecting = True
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
