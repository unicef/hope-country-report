from typing import Any, Dict
from django.core.management import BaseCommand, CommandError, CommandParser
from hope_country_report.config import env


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
            "--develop", action="store_true", help="Get values from the code, not from the current environment"
        )
        parser.add_argument(
            "--changed", action="store_true", help="Display only variables that have changed from defaults"
        )
        parser.add_argument(
            "--pattern",
            action="store",
            dest="pattern",
            default="{key}={value}  # {help}",
            help="Pattern for printing variables",
        )
        parser.add_argument(
            "--check", action="store_true", dest="check", default=False, help="Check for missing required variables"
        )
        parser.add_argument(
            "--ignore-errors", action="store_true", dest="ignore_errors", default=False, help="Ignore missing variables"
        )

    def handle(self, *args: "Any", **options: "Dict[str, Any]") -> None:
        check_failure = False
        pattern = options["pattern"]

        if options["check"]:
            self.stdout.write(self.style.SUCCESS("Checking for missing required environment variables..."))
            missing_vars = env.check_explicit()
            if missing_vars:
                for var in missing_vars:
                    self.stderr.write(self.style.ERROR(f"- Missing env variable: {var}"))
                    check_failure = True
            if check_failure and not options["ignore_errors"]:
                raise CommandError("One or more required environment variables are missing!")
            return

        for key, config in sorted(env.config.items()):
            help_text = config.get("help", "")
            default_value = config.get("default")
            # develop_value = config.get("develop")
            # explicit = config.get("explicit", False)
            if options["develop"]:
                value = env.get_develop_value(key)
            else:
                value = env.get_value(key)

            if options["changed"] and value == default_value:
                continue
            self.stdout.write(pattern.format(key=key, value=value, help=help_text, default=default_value))
