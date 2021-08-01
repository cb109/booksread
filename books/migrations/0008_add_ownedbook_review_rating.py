# Generated by Django 3.2 on 2021-08-01 09:20

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("books", "0007_ownedbook_read"),
    ]

    operations = [
        migrations.AddField(
            model_name="ownedbook",
            name="rating",
            field=models.PositiveIntegerField(
                default=0, validators=[django.core.validators.MaxValueValidator(9)]
            ),
        ),
        migrations.AddField(
            model_name="ownedbook",
            name="review",
            field=models.TextField(blank=True, default=""),
        ),
    ]