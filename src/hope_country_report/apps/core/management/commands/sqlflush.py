from typing import Any

from django.core.management.base import BaseCommand, CommandParser
from django.core.management.sql import sql_flush
from django.db import connections, DEFAULT_DB_ALIAS


class Command(BaseCommand):
    help = (
        "Returns a list of the SQL statements required to return all tables in "
        "the database to the state they were in just after they were installed."
    )

    output_transaction = True

    def add_arguments(self, parser: CommandParser) -> None:
        super().add_arguments(parser)
        parser.add_argument(
            "--database",
            default=DEFAULT_DB_ALIAS,
            help='Nominates a database to print the SQL for. Defaults to the "default" database.',
        )

    def handle(self, *args: Any, **options: Any) -> str | None:
        sql_statements = sql_flush(self.style, connections[options["database"]], allow_cascade=True)
        if not sql_statements and options["verbosity"] >= 1:
            self.stderr.write("No tables found.")
        return "\n".join(sql_statements)
