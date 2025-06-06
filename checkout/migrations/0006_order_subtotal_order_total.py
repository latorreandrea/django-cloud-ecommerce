# Generated by Django 5.2 on 2025-05-11 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0005_pendingorder'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='subtotal',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='order',
            name='total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
