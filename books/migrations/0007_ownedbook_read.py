# Generated by Django 3.2 on 2021-08-01 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0006_book_info_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='ownedbook',
            name='read',
            field=models.BooleanField(default=False),
        ),
    ]
