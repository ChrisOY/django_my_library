# Generated by Django 3.0.5 on 2020-04-15 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0006_auto_20200415_1454'),
    ]

    operations = [
        migrations.AlterField(
            model_name='language',
            name='name',
            field=models.CharField(help_text='Enter a book natural language (e.g. English, French, Japanese etc.', max_length=200),
        ),
    ]
