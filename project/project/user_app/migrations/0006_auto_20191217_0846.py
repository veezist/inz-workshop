# Generated by Django 2.2.6 on 2019-12-17 07:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0005_reservation_datetime_from'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='datetime_from',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='datetime_to',
            field=models.DateField(blank=True, null=True),
        ),
    ]
