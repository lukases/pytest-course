# Generated by Django 3.1.4 on 2023-10-07 01:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0006_auto_20231006_1858'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_limit',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
