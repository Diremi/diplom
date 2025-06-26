from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .models import EntrepreneurProfile, InvoiceItem, BankDetails
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email'
        
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username is not None and password:
            # Пробуем найти пользователя по email
            try:
                user = User.objects.get(email=username)
                self.user_cache = authenticate(
                    self.request,
                    username=user.username,
                    password=password
                )
                if self.user_cache is None:
                    raise forms.ValidationError(
                        self.error_messages['invalid_login'],
                        code='invalid_login',
                        params={'username': self.username_field.verbose_name},
                    )
                else:
                    self.confirm_login_allowed(self.user_cache)
            except User.DoesNotExist:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
        
        return self.cleaned_data
    
class EntrepreneurRegistrationForm(UserCreationForm):
    company_name = forms.CharField(
        label='Название ИП',
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Официальное название вашего ИП'
        })
    )
    
    inn = forms.CharField(
        label='ИНН',
        max_length=12,
        validators=[RegexValidator(r'^\d{12}$', 'ИНН должен содержать ровно 12 цифр')],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12-значный номер'
        })
    )
    
    ogrnip = forms.CharField(
        label='ОГРНИП',
        max_length=15,
        validators=[RegexValidator(r'^\d{15}$', 'ОГРНИП должен содержать ровно 15 цифр')],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '15-значный номер'
        })
    )
    
    phone = forms.CharField(
        label='Номер телефона',
        max_length=18,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7 (___) ___-__-__'
        })
    )
    
    email = forms.EmailField(
        label='Электронная почта',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@domain.ru'
        })
    )
    
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Убираем стандартное поле username
        if 'username' in self.fields:
            del self.fields['username']
        
        # Настройка полей паролей
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Не менее 8 символов'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Повторите пароль'
        })
    
    def clean_inn(self):
        inn = self.cleaned_data['inn']
        if EntrepreneurProfile.objects.filter(inn=inn).exists():
            raise forms.ValidationError('Предприниматель с таким ИНН уже зарегистрирован')
        return inn
    
    def clean_ogrnip(self):
        ogrnip = self.cleaned_data['ogrnip']
        if EntrepreneurProfile.objects.filter(ogrnip=ogrnip).exists():
            raise forms.ValidationError('Предприниматель с таким ОГРНИП уже зарегистрирован')
        return ogrnip
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже зарегистрирован')
        return email
    
    def generate_username(self):
        """Генерирует уникальное имя пользователя на основе ИНН"""
        inn = self.cleaned_data.get('inn', 'user')
        base_username = f"ip_{inn}"
        username = base_username
        counter = 1
        
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1
            
        return username
    
    def save(self, commit=True):
    # Создаем пользователя, но не сохраняем в БД пока
        user = super().save(commit=False)
        
        # Генерируем уникальное имя пользователя
        user.username = self.generate_username()
        user.email = self.cleaned_data['email']
        
        if commit:
            # Сохраняем пользователя
            user.save()
            
            # Для форм, унаследованных от UserCreationForm
            if hasattr(self, 'save_m2m'):
                self.save_m2m()
        
        return user
    
class BankDetailsForm(forms.ModelForm):
    class Meta:
        model = BankDetails
        fields = '__all__'
        exclude = ['entrepreneur']
        widgets = {
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bik': forms.TextInput(attrs={'class': 'form-control'}),
            'correspondent_account': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_account': forms.TextInput(attrs={'class': 'form-control'}),
        }

class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = '__all__'
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'vat_rate': forms.NumberInput(attrs={'class': 'form-control'}),
        }

InvoiceItemFormSet = forms.modelformset_factory(
    model=InvoiceItem,
    form=InvoiceItemForm,
    extra=1,
    can_delete=True
)

class InvoiceGenerationForm(forms.Form):
    customer_name = forms.CharField(
        label='Имя заказчика',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    customer_address = forms.CharField(
        label='Адрес заказчика',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    customer_inn = forms.CharField(
        label='ИНН заказчика',
        max_length=12,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        validators=[RegexValidator(r'^\d{10,12}$', 'ИНН должен содержать 10 или 12 цифр')]
    )
    date = forms.DateField(
        label='Дата счёта',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    payment_due_date = forms.DateField(
        label='Срок оплаты',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))