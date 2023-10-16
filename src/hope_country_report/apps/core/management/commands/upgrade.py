from typing import Any, Dict, TYPE_CHECKING

import logging
import os
import sys
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.management import BaseCommand, call_command
from django.core.management.base import CommandError, SystemCheckError
from django.core.validators import validate_email

from strategy_field.utils import fqn

from hope_country_report.apps.power_query.defaults import create_defaults
from hope_country_report.config import env

if TYPE_CHECKING:
    from argparse import ArgumentParser

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    requires_migrations_checks = False
    requires_system_checks = []

    def add_arguments(self, parser: "ArgumentParser") -> None:
        parser.add_argument(
            "--with-check",
            action="store_true",
            dest="check",
            default=False,
            help="Run checks",
        )
        parser.add_argument(
            "--no-check",
            action="store_false",
            dest="check",
            default=False,
            help="Do not run checks",
        )
        parser.add_argument(
            "--no-migrate",
            action="store_false",
            dest="migrate",
            default=True,
            help="Do not run migrations",
        )
        parser.add_argument(
            "--prompt",
            action="store_true",
            dest="prompt",
            default=False,
            help="Let ask for confirmation",
        )
        parser.add_argument(
            "--no-static",
            action="store_false",
            dest="static",
            default=True,
            help="Do not run collectstatic",
        )

        parser.add_argument(
            "--bootstrap",
            action="store_true",
            dest="bootstrap",
            default=False,
            help="Load Initial objects",
        )
        parser.add_argument(
            "--demo",
            action="store_true",
            dest="demo",
            default=False,
            help="Create demo Data",
        )
        parser.add_argument(
            "--admin-email",
            action="store",
            dest="admin_email",
            default="",
            help="Admin email",
        )
        parser.add_argument(
            "--admin-password",
            action="store",
            dest="admin_password",
            default="",
            help="Admin password",
        )

    def get_options(self, options: Dict[str, Any]) -> None:
        self.verbosity = options["verbosity"]
        self.run_check = options["check"]
        self.prompt = not options["prompt"]
        self.static = options["static"]
        self.migrate = options["migrate"]
        self.demo = options["demo"]
        self.bootstrap = options["bootstrap"]

        self.admin_email = str(options["admin_email"] or env("ADMIN_EMAIL", ""))
        self.admin_password = str(options["admin_password"] or env("ADMIN_PASSWORD", ""))

    def halt(self, msg: Any) -> None:  # pragma: no cover
        self.stdout.write(str(msg), style_func=self.style.ERROR)
        self.stdout.write("\n\n***", style_func=self.style.ERROR)
        self.stdout.write("SYSTEM HALTED", style_func=self.style.ERROR)
        self.stdout.write("Unable to start...", style_func=self.style.ERROR)
        sys.exit(1)

    def handle(self, *args: Any, **options: Any) -> None:
        from hope_country_report.apps.core.models import User

        self.get_options(options)
        if self.verbosity >= 1:
            echo = self.stdout.write
        else:
            echo = lambda *a, **kw: None

        try:
            extra = {
                "no_input": not self.prompt,
                "verbosity": self.verbosity - 1,
                "stdout": self.stdout,
            }
            echo("Running upgrade", style_func=self.style.WARNING)
            call_command("env", check=True)

            if self.run_check:
                call_command("check", deploy=True, verbosity=self.verbosity - 1)
            if self.static:
                static_root = Path(env("STATIC_ROOT"))
                echo(f"Run collectstatic to: '{static_root}' - '{static_root.absolute()}")
                if not static_root.exists():
                    static_root.mkdir(parents=True)
                call_command("collectstatic", **extra)

            if self.migrate:
                echo("Run migrations")
                call_command("migrate", **extra)
                call_command("create_extra_permissions")

            echo("Remove stale contenttypes")
            call_command("remove_stale_contenttypes", **extra)

            if self.admin_email:
                if User.objects.filter(email=self.admin_email).exists():
                    echo(
                        f"User {self.admin_email} found, skip creation",
                        style_func=self.style.WARNING,
                    )
                else:
                    echo("Creating superuser")
                    validate_email(self.admin_email)
                    os.environ["DJANGO_SUPERUSER_USERNAME"] = self.admin_email
                    os.environ["DJANGO_SUPERUSER_EMAIL"] = self.admin_email
                    os.environ["DJANGO_SUPERUSER_PASSWORD"] = self.admin_password
                    call_command(
                        "createsuperuser",
                        email=self.admin_email,
                        username=self.admin_email,
                        verbosity=self.verbosity - 1,
                        interactive=False,
                    )
            from hope_country_report.apps.core.utils import get_or_create_reporter_group

            echo("Create default group")
            get_or_create_reporter_group()
            from hope_country_report.apps.core.models import CountryOffice

            echo("Sync Country Offices")
            CountryOffice.sync()

            created = create_defaults()
            if not created:
                echo("WARNING:  default formatters not created")
            else:
                echo("Created default formatters")
                for f in created:
                    echo(f.name)
            echo("Create default PeriodicTask")
            from django_celery_beat.models import CrontabSchedule, PeriodicTask

            from hope_country_report.apps.power_query.celery_tasks import period_task_manager

            sunday, __ = CrontabSchedule.objects.get_or_create(day_of_week="0")
            first_of_month, __ = CrontabSchedule.objects.get_or_create(day_of_month="1")

            PeriodicTask.objects.get_or_create(
                name="Refresh every Sunday", defaults={"task": fqn(period_task_manager), "crontab": sunday}
            )

            PeriodicTask.objects.get_or_create(
                name="Refresh First Of Month", defaults={"task": fqn(period_task_manager), "crontab": first_of_month}
            )

            echo("Upgrade completed", style_func=self.style.SUCCESS)
        except ValidationError as e:
            self.halt("\n- ".join(["Wrong argument(s):", *e.messages]))
        except (CommandError, SystemCheckError) as e:
            self.halt(e)
        except Exception as e:
            self.stdout.write(str(e), style_func=self.style.ERROR)
            logger.exception(e)
            self.halt(e)
