# Generated by Django 2.2.7 on 2019-11-17 23:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0003_auto_20191113_1956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='objectivity',
            field=models.FloatField(blank=True, default=0, editable=False),
        ),
    ]
