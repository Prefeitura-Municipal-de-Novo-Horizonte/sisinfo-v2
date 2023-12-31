# Generated by Django 4.2.7 on 2023-12-04 15:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bidding_supplier", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contact",
            name="value",
            field=models.CharField(max_length=255, verbose_name="contato"),
        ),
        migrations.AlterField(
            model_name="supplier",
            name="cnpj",
            field=models.CharField(blank=True, max_length=14, verbose_name="CNPJ"),
        ),
        migrations.AlterField(
            model_name="supplier",
            name="company",
            field=models.CharField(
                blank=True, max_length=200, unique=True, verbose_name="Razão social"
            ),
        ),
    ]
