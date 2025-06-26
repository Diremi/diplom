from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class EntrepreneurProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='entrepreneur_profile',
        verbose_name='Пользователь'
    )
    
    
    company_name = models.CharField(
        max_length=255,
        verbose_name='Название ИП',
        help_text='Официальное название индивидуального предпринимателя'
    )
    
    inn = models.CharField(
        max_length=12,
        validators=[RegexValidator(r'^\d{12}$', 'ИНН должен содержать ровно 12 цифр')],
        verbose_name='ИНН',
        unique=True,
        help_text='12-значный идентификационный номер налогоплательщика'
    )
    
    ogrnip = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\d{15}$', 'ОГРНИП должен содержать ровно 15 цифр')],
        verbose_name='ОГРНИП',
        unique=True,
        help_text='15-значный основной государственный регистрационный номер'
    )
    
    phone = models.CharField(
        max_length=18,
        verbose_name='Номер телефона',
        help_text='Формат: +7 (XXX) XXX-XX-XX'
    )
    
    
    is_verified = models.BooleanField(
        default=False,
        verbose_name='Профиль верифицирован'
    )
    
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания профиля'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата последнего обновления'
    )

    class Meta:
        verbose_name = 'Профиль предпринимателя'
        verbose_name_plural = 'Профили предпринимателей'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.company_name} (ИНН: {self.inn})"

class BankDetails(models.Model):
    entrepreneur = models.OneToOneField(
        EntrepreneurProfile,
        on_delete=models.CASCADE,
        related_name='bank_details',
        verbose_name='Предприниматель'
    )
    
    bank_name = models.CharField(
        max_length=255,
        verbose_name='Название банка'
    )
    
    bik = models.CharField(
        max_length=9,
        validators=[RegexValidator(r'^\d{9}$', 'БИК должен содержать ровно 9 цифр')],
        verbose_name='БИК'
    )
    
    correspondent_account = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^\d{20}$', 'Корреспондентский счёт должен содержать ровно 20 цифр')],
        verbose_name='Корреспондентский счёт'
    )
    
    payment_account = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^\d{20}$', 'Расчётный счёт должен содержать ровно 20 цифр')],
        verbose_name='Расчётный счёт'
    )
    
    class Meta:
        verbose_name = 'Банковские реквизиты'
        verbose_name_plural = 'Банковские реквизиты'
    
    def __str__(self):
        return f"Реквизиты {self.entrepreneur.company_name}"

class InvoiceItem(models.Model):
    description = models.CharField(max_length=255, verbose_name='Наименование товара/услуги')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Количество')
    unit = models.CharField(max_length=20, verbose_name='Единица измерения')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена за единицу')
    vat_rate = models.DecimalField(max_digits=4, decimal_places=2, default=0, verbose_name='Ставка НДС (%)')
    
    class Meta:
        verbose_name = 'Позиция счёта'
        verbose_name_plural = 'Позиции счёта'
    
    def __str__(self):
        return self.description

class GeneratedDocument(models.Model):
    entrepreneur = models.ForeignKey(
        EntrepreneurProfile,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Предприниматель'
    )
    
    document_type = models.CharField(max_length=50, verbose_name='Тип документа')
    file = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name='Файл')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Сгенерированный документ'
        verbose_name_plural = 'Сгенерированные документы'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.document_type} от {self.created_at.strftime('%d.%m.%Y')}"