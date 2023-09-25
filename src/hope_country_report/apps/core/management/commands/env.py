import os
import uuid

from django.core.management import BaseCommand, CommandError


class Command(BaseCommand):
    requires_migrations_checks = False
    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument(
            "--template", action="store_true", dest="template", default=False, help="Only dumps keys, without values"
        )
        parser.add_argument(
            "--group",
            choices=("mandatory", "optional", "all", "develop"),
            default="mandatory",
            help="Dump all or partial keys",
        )
        parser.add_argument(
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

    def handle(self, *args, **options):
        from hope_country_report.config import MANDATORY, OPTIONAL

        if options["comment"] and options["group"] not in ["all", "develop"]:
            raise CommandError("Please use `--group all` with `--comment-optinal`")

        VARIABLES = {**MANDATORY, **OPTIONAL}

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
        pattern = "{key}={value}"
        if options["style"] == "direnv":
            pattern = "export {key}={value}"
        elif options["style"] == "dotenv":
            pattern = "export {key}=${{{key}}}"

        for k, v in sorted(selected.items()):
            if options["template"]:
                value = ""
            elif options["defaults"]:
                value = VARIABLES[k][1]
            else:
                value = os.environ.get(k, "")

            if options["check"]:
                try:
                    os.environ[k]
                except KeyError:
                    self.stderr.write(self.style.ERROR(f"- Missing env variable: {k}"))
                    check_failure = True
            else:
                if k in OPTIONAL.keys() and options["comment"]:
                    self.stdout.write(("# %s" % pattern).format(key=k, value=value))
                else:
                    self.stdout.write(pattern.format(key=k, value=value))

        if check_failure:
            raise CommandError("Env check command failure!")
