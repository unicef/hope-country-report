from typing import TYPE_CHECKING

import os
import uuid

from django.core.management import BaseCommand, CommandError, CommandParser

if TYPE_CHECKING:
    from typing import Any, Dict


class Command(BaseCommand):
    requires_migrations_checks = False
    requires_system_checks = []

    def add_arguments(self, parser: "CommandParser") -> None:
        parser.add_argument(
            "-t",
            "--template",
            action="store_true",
            dest="template",
            default=False,
            help="Only dumps keys, without values",
        )
        parser.add_argument(
            "-g",
            "--group",
            choices=("mandatory", "optional", "all", "develop"),
            default="mandatory",
            help="Dump all or partial keys",
        )
        parser.add_argument(
            "-s",
            "--style",
            choices=("dotenv", "direnv", "env"),
            default="env",
            help="Format dump according to specific synthax",
        )
        parser.add_argument(
            "--defaults", action="store_true", help="Get values from teh code not from the current environment"
        )
        parser.add_argument(
            "--comment-optional", action="store_true", dest="comment", default=False, help="Comment optional"
        )
        parser.add_argument(
            "--check", action="store_true", dest="check", default=False, help="Check env for variable availability"
        )

    def handle(self, *args: "Any", **options: "Any") -> None:
        from hope_country_report.config import MANDATORY, OPTIONAL

        VARIABLES: "Dict[str, Any]" = {**MANDATORY, **OPTIONAL}

        DEVELOP = {
            "DEBUG": True,
            "SECRET_KEY": uuid.uuid4(),
            **{
                k: VARIABLES[k][1]
                for k in [
                    "CELERY_BROKER_URL",
                    "DATABASE_URL",
                ]
            },
        }
        selected = {}
        if options["group"] == "all":
            selected.update(**VARIABLES)
        elif options["group"] == "mandatory":
            selected.update(**MANDATORY)
        elif options["group"] == "optional":
            selected.update(**OPTIONAL)
        elif options["group"] == "develop":
            selected.update(**DEVELOP)

        check_failure = False
        pattern = "{key}={value}{help}"
        if options["style"] == "direnv":
            pattern = "export {key}={value}{help}"
        elif options["style"] == "dotenv":
            pattern = "export {key}=${{{key}}}"
        value: Any
        help: str

        for k, __ in sorted(selected.items()):
            help = ""
            if options["template"]:
                value = ""
            elif options["defaults"]:
                value = VARIABLES[k][1]
                if len(VARIABLES[k]) > 2:
                    help = f"  # {VARIABLES[k][2]}"
            else:
                value = os.environ.get(k, VARIABLES[k][1])
                if len(VARIABLES[k]) > 2:
                    help = f"  # {VARIABLES[k][2]}"

            if options["check"]:
                try:
                    os.environ[k]
                except KeyError:
                    self.stderr.write(self.style.ERROR(f"- Missing env variable: {k}"))
                    check_failure = True
            else:
                if k in OPTIONAL.keys() and options["comment"]:
                    self.stdout.write(("# %s" % pattern).format(key=k, value=value, help=help))
                else:
                    self.stdout.write(pattern.format(key=k, value=value, help=help))

        if check_failure:
            raise CommandError("Env check command failure!")
