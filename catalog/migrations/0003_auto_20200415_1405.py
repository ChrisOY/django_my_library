# Generated by Django 3.0.5 on 2020-04-15 14:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_auto_20200415_1254'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='language',
            options={'ordering': ['name']},
        ),
    ]
