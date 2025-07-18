# Generated by Django 5.2.3 on 2025-07-09 19:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('menu', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('logo', models.ImageField(blank=True, null=True, upload_to='restaurant_logos/')),
                ('banner', models.ImageField(blank=True, null=True, upload_to='restaurant_banners/')),
                ('address', models.CharField(max_length=255)),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('phone_number', models.CharField(blank=True, max_length=20)),
                ('paylink_account_id', models.CharField(blank=True, max_length=255, null=True, verbose_name='PayLink Account ID')),
                ('average_rating', models.DecimalField(decimal_places=2, default=0.0, max_digits=3, verbose_name='Средний рейтинг')),
                ('review_count', models.PositiveIntegerField(default=0, verbose_name='Количество отзывов')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('categories', models.ManyToManyField(related_name='restaurants', to='menu.menucategory')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='restaurants', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DeliveryTariff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('base_fee', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Базовая стоимость')),
                ('fee_per_km', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Стоимость за км')),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tariffs', to='restaurants.restaurant')),
            ],
        ),
    ]
