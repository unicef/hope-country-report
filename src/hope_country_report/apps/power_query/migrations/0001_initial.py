# Generated by Django 4.2.6 on 2023-10-16 18:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import hope_country_report.apps.power_query.json
import hope_country_report.apps.power_query.models
import strategy_field.fields
import taggit.managers


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.POWER_QUERY_PROJECT_MODEL),
        ("django_celery_beat", "0018_improve_crontab_helptext"),
        ("contenttypes", "0002_remove_content_type_name"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("taggit", "0005_auto_20220424_2025"),
    ]

    operations = [
        migrations.CreateModel(
            name="Project",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
            ],
            options={
                "swappable": "POWER_QUERY_PROJECT_MODEL",
            },
        ),
        migrations.CreateModel(
            name="Formatter",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, unique=True)),
                ("code", models.TextField(blank=True, null=True)),
                (
                    "content_type",
                    models.CharField(
                        choices=[
                            (".json", "application/json"),
                            (".pdf", "application/pdf"),
                            (".png", "image/png"),
                            (".csv", "text/csv"),
                            (".html", "text/html"),
                            (".txt", "text/plain"),
                            (".xml", "application/xml"),
                            (".xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
                            (".docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
                        ],
                        max_length=5,
                    ),
                ),
                (
                    "processor",
                    strategy_field.fields.StrategyField(
                        default="hope_country_report.apps.power_query.processors.ToHTML"
                    ),
                ),
                ("type", models.IntegerField(choices=[(1, "List"), (2, "Detail")], default=1)),
                (
                    "project",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.POWER_QUERY_PROJECT_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Parametrizer",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.SlugField(editable=False, max_length=255, unique=True)),
                ("name", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True, max_length=255, null=True)),
                (
                    "value",
                    models.JSONField(
                        default=dict, validators=[hope_country_report.apps.power_query.models.validate_queryargs]
                    ),
                ),
                ("system", models.BooleanField(blank=True, default=False, editable=False)),
                (
                    "project",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.POWER_QUERY_PROJECT_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Arguments",
                "verbose_name_plural": "Arguments",
            },
        ),
        migrations.CreateModel(
            name="Query",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("celery_task", models.CharField(blank=True, max_length=36, null=True)),
                ("name", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("code", models.TextField(blank=True, default="result=conn.all()")),
                (
                    "info",
                    models.JSONField(
                        blank=True, default=dict, encoder=hope_country_report.apps.power_query.json.PQJSONEncoder
                    ),
                ),
                ("sentry_error_id", models.CharField(blank=True, max_length=400, null=True)),
                ("error_message", models.CharField(blank=True, max_length=400, null=True)),
                ("last_run", models.DateTimeField(blank=True, null=True)),
                ("active", models.BooleanField(default=True)),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="queries",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "parametrizer",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="power_query.parametrizer",
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="power_query.query"
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.POWER_QUERY_PROJECT_MODEL,
                    ),
                ),
                (
                    "target",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="contenttypes.contenttype"),
                ),
            ],
            options={
                "verbose_name_plural": "Queries",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Report",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("celery_task", models.CharField(blank=True, max_length=36, null=True)),
                ("title", models.CharField(max_length=255, verbose_name="Report Title")),
                ("name", models.CharField(blank=True, max_length=255, null=True)),
                ("active", models.BooleanField(default=True)),
                ("last_run", models.DateTimeField(blank=True, null=True)),
                ("validity_days", models.IntegerField(default=365)),
                (
                    "formatter",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="power_query.formatter"
                    ),
                ),
                ("limit_access_to", models.ManyToManyField(blank=True, related_name="+", to=settings.AUTH_USER_MODEL)),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.POWER_QUERY_PROJECT_MODEL,
                    ),
                ),
                ("query", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="power_query.query")),
                (
                    "schedule",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="django_celery_beat.periodictask",
                    ),
                ),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        blank=True,
                        help_text="A comma-separated list of tags.",
                        through="taggit.TaggedItem",
                        to="taggit.Tag",
                        verbose_name="Tags",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ReportTemplate",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ("doc", models.FileField(upload_to="")),
                ("suffix", models.CharField(max_length=20)),
                (
                    "content_type",
                    models.CharField(
                        choices=[
                            (".json", "application/json"),
                            (".pdf", "application/pdf"),
                            (".png", "image/png"),
                            (".csv", "text/csv"),
                            (".html", "text/html"),
                            (".txt", "text/plain"),
                            (".xml", "application/xml"),
                            (".xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
                            (".docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
                        ],
                        max_length=200,
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.POWER_QUERY_PROJECT_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="parametrizer",
            name="source",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="power_query.query",
            ),
        ),
        migrations.AddField(
            model_name="formatter",
            name="template",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="power_query.reporttemplate"
            ),
        ),
        migrations.CreateModel(
            name="Dataset",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("hash", models.CharField(editable=False, max_length=200, unique=True)),
                ("last_run", models.DateTimeField(blank=True, null=True)),
                ("description", models.CharField(max_length=100)),
                ("value", models.BinaryField(blank=True, null=True)),
                ("file", models.FileField(blank=True, null=True, upload_to="datasets")),
                ("size", models.IntegerField(default=0)),
                ("info", models.JSONField(blank=True, default=dict)),
                (
                    "extra",
                    models.BinaryField(blank=True, help_text="Any other attribute to pass to the formatter", null=True),
                ),
                (
                    "query",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="datasets", to="power_query.query"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ReportDocument",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("timestamp", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=300)),
                ("output", models.BinaryField(blank=True, null=True)),
                (
                    "arguments",
                    models.JSONField(default=dict, encoder=hope_country_report.apps.power_query.json.PQJSONEncoder),
                ),
                (
                    "content_type",
                    models.CharField(
                        choices=[
                            (".json", "application/json"),
                            (".pdf", "application/pdf"),
                            (".png", "image/png"),
                            (".csv", "text/csv"),
                            (".html", "text/html"),
                            (".txt", "text/plain"),
                            (".xml", "application/xml"),
                            (".xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
                            (".docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
                        ],
                        max_length=5,
                    ),
                ),
                ("info", models.JSONField(blank=True, default=dict)),
                ("dataset", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="power_query.dataset")),
                ("limit_access_to", models.ManyToManyField(blank=True, related_name="+", to=settings.AUTH_USER_MODEL)),
                (
                    "report",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="documents", to="power_query.report"
                    ),
                ),
            ],
            options={
                "unique_together": {("report", "dataset")},
            },
        ),
    ]