# Generated by Django 5.1.6 on 2025-03-05 12:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0001_initial'),
        ('workspace', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='job_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='workspace.meshmodel'),
        ),
    ]
