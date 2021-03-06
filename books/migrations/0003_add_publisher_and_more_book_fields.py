# Generated by Django 3.2 on 2021-04-17 20:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("books", "0002_add_book_author_ownedbook"),
    ]

    operations = [
        migrations.CreateModel(
            name="Publisher",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=128)),
            ],
        ),
        migrations.AddField(
            model_name="book", name="description", field=models.TextField(default=""),
        ),
        migrations.AddField(
            model_name="book", name="num_pages", field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="book",
            name="publisher",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="books",
                to="books.publisher",
            ),
        ),
    ]
