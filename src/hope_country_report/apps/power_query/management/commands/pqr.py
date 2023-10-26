from typing import Any

from django.core.management import BaseCommand, CommandError, CommandParser

from hope_country_report.apps.power_query.models import Report


class Command(BaseCommand):
    requires_migrations_checks = False

    def add_arguments(self, parser: CommandParser) -> None:
        subparsers = parser.add_subparsers(title="command", dest="command", required=True)
        CommandParser(add_help=False)
        test = subparsers.add_parser("test")
        test.add_argument("filename")
        test.add_argument("--target")

        execute = subparsers.add_parser("execute")
        execute.add_argument("id")
        execute.add_argument(
            "--persist",
            action="store_true",
            default=False,
        )

        run = subparsers.add_parser("run")
        run.add_argument("id")
        run.add_argument(
            "--persist",
            action="store_true",
            default=True,
        )
        run.add_argument(
            "--arguments",
            "-a",
            action="store",
            nargs="+",
            default=[],
        )

        subparsers.add_parser("list")

    def _list(self, *args: Any, **options: Any) -> None:
        from hope_country_report.apps.power_query.models import Report

        line = "#{id:>5}   {name:<32} {status:<25} {last_run} "
        self.stdout.write(line.format(id="id", name="name", status="status", last_run="last run"))
        for q in Report.objects.all():
            self.stdout.write(line.format(id=q.id, name=q.name[:30], status=q.status, last_run=q.last_run))

    def _run(self, *args: Any, **options: Any) -> None:
        try:
            r: Report = Report.objects.get(pk=options["id"])
            result = r.execute()
            for entry in result:
                self.stdout.write(str(entry))
        except Exception as e:
            self.stdout.write(f"Error: {e.__class__.__name__}")
            self.stdout.write(str(e))
            raise

    def handle(self, *args: Any, **options: Any) -> None:
        cmd = options["command"]
        if cmd == "list":
            self._list(*args, **options)
        elif cmd == "run":
            self._run(*args, **options)
        else:
            raise CommandError(cmd)
