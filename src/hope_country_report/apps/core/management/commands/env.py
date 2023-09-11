import os
from typing import Any, TYPE_CHECKING

from django.core.management import BaseCommand, CommandError

if TYPE_CHECKING:
    from argparse import ArgumentParser


class Command(BaseCommand):
    def add_arguments(self, parser: "ArgumentParser") -> None:
        parser.add_argument(
            "--no-mandatory",
            action="store_false",
            dest="mandatory",
            default=True,
            help="Do not dump mandatory",
        )
        parser.add_argument(
            "--no-optional",
            action="store_false",
            dest="optional",
            default=True,
            help="Do not dump optional",
        )
        parser.add_argument(
            "--no-values",
            action="store_false",
            dest="values",
            default=True,
            help="Do not dump values",
        )
        parser.add_argument(
            "--comment-optional",
            action="store_true",
            dest="comment",
            default=False,
            help="Comment optional",
        )
        parser.add_argument(
            "--current",
            action="store_true",
            dest="current",
            default=False,
            help="Dump current values",
        )
        parser.add_argument(
            "--vars",
            action="store_true",
            dest="vars",
            default=False,
            help="Dump current values",
        )
        parser.add_argument(
            "--no-empty",
            action="store_true",
            dest="no_empty",
            default=False,
            help="Do not dump empty values",
        )
        parser.add_argument(
            "--config",
            action="store_true",
            dest="config",
            default=False,
            help="Create .env/.envrc",
        )
        parser.add_argument(
            "--check",
            action="store_true",
            dest="check",
            default=False,
            help="Check env for variable availability",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        from hope_country_report.config import env, MANDATORY, OPTIONS

        environment = {}
        if options["mandatory"]:
            environment.update(**MANDATORY)
        if options["optional"]:
            environment.update(**OPTIONS)
        check_failure = False
        for k, __ in sorted(environment.items()):
            if options["vars"]:
                value = "${%s}" % k
            elif options["current"]:
                value = os.environ.get(k, "")
            elif options["values"]:
                value = env(k)
            else:
                value = ""
            # if value or not options["no_empty"]:
            #     if options["comment"] and k in OPTIONS.keys():
            #         self.stdout.write(f"#{k}={value}")
            #     else:
            #         self.stdout.write(f"{k}={value}")

            if options["check"]:
                try:
                    os.environ[k]
                except KeyError:
                    if k in MANDATORY:
                        self.stderr.write(self.style.ERROR(f"- Missing env variable: {k}"))
                        check_failure = True
            elif value or not options["no_empty"]:
                if options["comment"] and k in OPTIONS.keys():
                    self.stdout.write(f"#{k}={value}")
                else:
                    self.stdout.write(f"{k}={value}")

        if check_failure:
            raise CommandError("Env check command failure!")
