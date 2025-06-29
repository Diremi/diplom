# Generated by Django 5.2.2 on 2025-06-08 21:24

import django.core.validators
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
            name='EntrepreneurProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(help_text='Официальное название индивидуального предпринимателя', max_length=255, verbose_name='Название ИП')),
                ('inn', models.CharField(help_text='12-значный идентификационный номер налогоплательщика', max_length=12, unique=True, validators=[django.core.validators.RegexValidator('^\\d{12}$', 'ИНН должен содержать ровно 12 цифр')], verbose_name='ИНН')),
                ('ogrnip', models.CharField(help_text='15-значный основной государственный регистрационный номер', max_length=15, unique=True, validators=[django.core.validators.RegexValidator('^\\d{15}$', 'ОГРНИП должен содержать ровно 15 цифр')], verbose_name='ОГРНИП')),
                ('phone', models.CharField(help_text='Формат: +7 (XXX) XXX-XX-XX', max_length=18, verbose_name='Номер телефона')),
                ('is_verified', models.BooleanField(default=False, verbose_name='Профиль верифицирован')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания профиля')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата последнего обновления')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='entrepreneur_profile', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Профиль предпринимателя',
                'verbose_name_plural': 'Профили предпринимателей',
                'ordering': ['-created_at'],
            },
        ),
    ]
