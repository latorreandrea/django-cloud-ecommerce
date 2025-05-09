# Generated by Django 5.2 on 2025-04-29 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_product_cost'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productimage',
            name='image',
        ),
        migrations.AddField(
            model_name='productimage',
            name='large_image',
            field=models.URLField(blank=True, max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='productimage',
            name='small_image',
            field=models.URLField(blank=True, max_length=1000, null=True),
        ),
    ]
