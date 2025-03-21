# Generated by Django 5.1.6 on 2025-03-18 08:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MeshPromptModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_id', models.CharField(max_length=255, unique=True)),
                ('status', models.CharField(default='processing', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('create_prompt', models.TextField()),
                ('art_style', models.CharField(default='realistic', max_length=50)),
                ('image_path', models.FileField(blank=True, null=True, upload_to='')),
                ('video_path', models.FileField(blank=True, null=True, upload_to='')),
                ('fbx_path', models.FileField(blank=True, null=True, upload_to='')),
                ('glb_path', models.FileField(blank=True, null=True, upload_to='')),
                ('obj_path', models.FileField(blank=True, null=True, upload_to='')),
                ('usdz_path', models.FileField(blank=True, null=True, upload_to='')),
                ('metadata_path', models.FileField(blank=True, null=True, upload_to='')),
                ('base_color_path', models.FileField(blank=True, null=True, upload_to='')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
