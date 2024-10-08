# Generated by Django 5.0.6 on 2024-09-19 13:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_places_like_count_subplaces_like_count_like_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='places',
            name='like_count',
        ),
        migrations.RemoveField(
            model_name='subplaces',
            name='like_count',
        ),
        migrations.CreateModel(
            name='LikePlace',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('place_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.places')),
                ('user_like', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='Like',
        ),
    ]
