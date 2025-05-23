from typing import Any

from pathlib import Path

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand, CommandError, CommandParser

from hope_country_report.apps.power_query.models import Query as PowerQuery


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
        queue = subparsers.add_parser("queue")
        queue.add_argument("id")

        check = subparsers.add_parser("check")
        check.add_argument("id")

        run = subparsers.add_parser("run")
        run.add_argument("id")
        run.add_argument(
            "--persist",
            action="store_true",
            default=False,
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
        from hope_country_report.apps.power_query.models import Query as PowerQuery

        line = "#{id:>5}   {name:<32} {status:<25} {last_run} "
        self.stdout.write(line.format(id="id", name="name", status="status", last_run="last run"))
        for q in PowerQuery.objects.all():
            self.stdout.write(line.format(id=q.id, name=q.name[:30], status=q.status, last_run=q.last_run))

    def _test(self, *args: Any, **options: Any) -> None:
        code = Path(options["filename"]).read_text()
        target = options["target"]
        model = ContentType.objects.get_for_model(apps.get_model(target))
        pq = PowerQuery(name="Test", target=model, code=code)
        arguments = {}
        result, info = pq.run(persist=False, arguments=arguments)
        for _entry in result:
            pass

    def _check(self, *args: Any, **options: Any) -> None:
        PowerQuery.objects.get(pk=options["id"])

    def _queue(self, *args: Any, **options: Any) -> None:
        pq = PowerQuery.objects.get(pk=options["id"])
        pq.queue()
        pq.refresh_from_db()

    def _run(self, *args: Any, **options: Any) -> None:
        query_args: dict[str, str] = {}
        try:
            for a in options["arguments"]:
                k, v = a.split("=")
                query_args[k] = v
            pq = PowerQuery.objects.get(pk=options["id"])
            result, info = pq.run(persist=options["persist"], arguments=query_args)
            for k, v in info.items():
                self.stdout.write(f"{k}: {v}")
            self.stdout.write("=" * 80)
            for entry in result:
                self.stdout.write(str(entry))
        except Exception as e:
            self.stdout.write(f"Error: {e.__class__.__name__}")
            self.stdout.write(str(e))

    def _execute(self, *args: Any, **options: Any) -> None:
        try:
            pq = PowerQuery.objects.get(pk=options["id"])
            result = pq.execute_matrix(persist=options["persist"])
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
        elif cmd == "execute":
            self._execute(*args, **options)
        elif cmd == "test":
            self._test(*args, **options)
        elif cmd == "run":
            self._run(*args, **options)
        elif cmd == "queue":
            self._queue(*args, **options)
        elif cmd == "check":
            self._check(*args, **options)
        else:
            raise CommandError(cmd)
