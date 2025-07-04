# Generated by Django 5.2.3 on 2025-06-29 22:03

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
            name='CourierProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_card_photo', models.ImageField(upload_to='courier_documents/', verbose_name='Фото удостоверения')),
                ('driver_license_photo', models.ImageField(blank=True, null=True, upload_to='courier_documents/', verbose_name='Фото водит. прав')),
                ('verification_status', models.CharField(choices=[('not_submitted', 'Не подано'), ('on_review', 'На проверке'), ('approved', 'Одобрено'), ('rejected', 'Отклонено')], default='not_submitted', max_length=20, verbose_name='Статус верификации')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='courier_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Профиль курьера',
                'verbose_name_plural': 'Профили курьеров',
            },
        ),
    ]
