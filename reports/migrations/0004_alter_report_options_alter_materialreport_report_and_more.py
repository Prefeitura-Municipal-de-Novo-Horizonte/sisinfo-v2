# Generated by Django 4.2.7 on 2023-12-11 18:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0003_alter_report_options_alter_report_pro_accountable_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='report',
            options={'ordering': ['-created_at', 'status', '-updated_at'], 'verbose_name': 'laudo', 'verbose_name_plural': 'laudos'},
        ),
        migrations.AlterField(
            model_name='materialreport',
            name='report',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='laudos', to='reports.report', verbose_name='laudo'),
        ),
        migrations.AlterField(
            model_name='report',
            name='status',
            field=models.CharField(choices=[('1', 'Aberto'), ('2', 'Aguardando'), ('3', 'Finalizado')], default=1, max_length=1, verbose_name='status'),
        ),
    ]
