# Generated by Django 5.1.3 on 2024-11-07 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("power_query", "0008_alter_formatter_file_suffix"),
    ]

    operations = [
        migrations.AlterField(
            model_name="formatter",
            name="file_suffix",
            field=models.CharField(
                choices=[
                    (".json", "application/json"),
                    (".pdf", "application/pdf"),
                    (".xls", "application/vnd.ms-excel"),
                    (".zip", "application/x-zip-compressed"),
                    (".png", "image/png"),
                    (".csv", "text/csv"),
                    (".html", "text/html"),
                    (".txt", "text/plain"),
                    (".xml", "text/xml"),
                    (".xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
                    (".docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
                    (".yaml", "text/vnd.yaml"),
                ],
                max_length=10,
            ),
        ),
    ]