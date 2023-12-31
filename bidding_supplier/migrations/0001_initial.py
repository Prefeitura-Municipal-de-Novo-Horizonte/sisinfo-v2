# Generated by Django 4.2.7 on 2023-11-29 17:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.CharField(blank=True, max_length=200, unique=True, verbose_name='razão social')),
                ('trade', models.CharField(blank=True, max_length=255, null=True, verbose_name='nome fantasia')),
                ('cnpj', models.CharField(blank=True, max_length=14, verbose_name='cnpj')),
                ('slug', models.SlugField(verbose_name='slug')),
                ('address', models.TextField(blank=True, null=True, verbose_name='endereço')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='atualizado em')),
            ],
            options={
                'verbose_name': 'fornecedor',
                'verbose_name_plural': 'fornecedores',
            },
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(choices=[('E', 'Email'), ('P', 'Telefone')], max_length=1, verbose_name='tipo')),
                ('value', models.CharField(max_length=255, verbose_name='valor')),
                ('whatsapp', models.BooleanField(default=False, verbose_name='whatsapp')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='suppliers', to='bidding_supplier.supplier', verbose_name='fornecedor')),
            ],
            options={
                'verbose_name': 'contato',
                'verbose_name_plural': 'contatos',
            },
        ),
    ]
