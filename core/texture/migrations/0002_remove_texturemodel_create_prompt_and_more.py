# Generated by Django 5.1.6 on 2025-03-12 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("texture", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="texturemodel",
            name="create_prompt",
        ),
        migrations.RemoveField(
            model_name="texturemodel",
            name="fbx_path",
        ),
        migrations.RemoveField(
            model_name="texturemodel",
            name="glb_path",
        ),
        migrations.RemoveField(
            model_name="texturemodel",
            name="image_path",
        ),
        migrations.RemoveField(
            model_name="texturemodel",
            name="metadata_path",
        ),
        migrations.RemoveField(
            model_name="texturemodel",
            name="obj_path",
        ),
        migrations.RemoveField(
            model_name="texturemodel",
            name="usdz_path",
        ),
        migrations.RemoveField(
            model_name="texturemodel",
            name="video_path",
        ),
        migrations.AddField(
            model_name="texturemodel",
            name="art_style",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="texturemodel",
            name="base_color_url",
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="texturemodel",
            name="expires_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="texturemodel",
            name="fbx_url",
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="texturemodel",
            name="finished_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="texturemodel",
            name="glb_url",
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="texturemodel",
            name="metallic_url",
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="texturemodel",
            name="name",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="texturemodel",
            name="negative_prompt",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="texturemodel",
            name="normal_url",
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="texturemodel",
            name="obj_url",
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="texturemodel",
            name="object_prompt",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="texturemodel",
            name="progress",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="texturemodel",
            name="roughness_url",
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="texturemodel",
            name="started_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="texturemodel",
            name="style_prompt",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="texturemodel",
            name="task_error",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="texturemodel",
            name="texture_prompt",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="texturemodel",
            name="thumbnail_url",
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="texturemodel",
            name="usdz_url",
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="texturemodel",
            name="created_at",
            field=models.DateTimeField(),
        ),
    ]
