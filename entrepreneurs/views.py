from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from .forms import EntrepreneurRegistrationForm
from django.contrib.auth.views import LoginView
from .forms import CustomAuthenticationForm  
from django.http import HttpResponse, FileResponse
from .models import EntrepreneurProfile, BankDetails, GeneratedDocument, InvoiceItem
from .forms import BankDetailsForm, InvoiceItemFormSet, InvoiceGenerationForm
from .documents import generate_invoice
from django.contrib import messages
import os
from datetime import datetime

class CustomLoginView(LoginView):
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse('entrepreneurs:dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['home_url'] = reverse('entrepreneurs:home')
        return context

class CustomLogoutView(LogoutView):
    
    @method_decorator(require_POST)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    

def home_page(request):
    return render(request, 'home.html')

def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('entrepreneurs:dashboard')
    else:
        return redirect('entrepreneurs:login')

def register_entrepreneur(request):
    if request.method == 'POST':
        form = EntrepreneurRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            EntrepreneurProfile.objects.create(
                user=user,
                company_name=form.cleaned_data['company_name'],
                inn=form.cleaned_data['inn'],
                ogrnip=form.cleaned_data['ogrnip'],
                phone=form.cleaned_data['phone']
            )
            
            user = authenticate(
                username=user.username,
                password=form.cleaned_data['password1']
            )
            
            if user is not None:
                login(request, user)
                return redirect('entrepreneurs:dashboard')
    else:
        form = EntrepreneurRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    try:
        profile = request.user.entrepreneur_profile
    except EntrepreneurProfile.DoesNotExist:
        return redirect('profile_create')
    
    return render(request, 'dashboard.html', {
        'user': request.user,
        'profile': profile
    })

@login_required
def bank_details(request):
    entrepreneur = get_object_or_404(EntrepreneurProfile, user=request.user)
    
    try:
        bank_details = entrepreneur.bank_details
    except BankDetails.DoesNotExist:
        bank_details = None
    
    if request.method == 'POST':
        form = BankDetailsForm(request.POST, instance=bank_details)
        if form.is_valid():
            bank_details = form.save(commit=False)
            bank_details.entrepreneur = entrepreneur
            bank_details.save()
            messages.success(request, 'Банковские реквизиты успешно сохранены!')
            return redirect('entrepreneurs:documents')
    else:
        form = BankDetailsForm(instance=bank_details)
    
    return render(request, 'entrepreneurs/bank_details.html', {
        'form': form,
        'entrepreneur': entrepreneur
    })

@login_required
def create_invoice(request):
    entrepreneur = get_object_or_404(EntrepreneurProfile, user=request.user)
    
    try:
        bank_details = entrepreneur.bank_details
    except BankDetails.DoesNotExist:
        messages.warning(request, 'Пожалуйста, сначала заполните банковские реквизиты!')
        return redirect('entrepreneurs:bank_details')
    
    if request.method == 'POST':
        form = InvoiceGenerationForm(request.POST)
        formset = InvoiceItemFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            items_data = []
            for item_form in formset:
                if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                    cleaned_data = item_form.cleaned_data.copy()
                    # Преобразуем Decimal в float для сериализации
                    cleaned_data['quantity'] = float(cleaned_data['quantity'])
                    cleaned_data['price'] = float(cleaned_data['price'])
                    cleaned_data['vat_rate'] = float(cleaned_data['vat_rate'])
                    items_data.append(cleaned_data)
            
            form_data = form.cleaned_data.copy()
            # Преобразуем даты в строки
            form_data['date'] = form_data['date'].isoformat()
            form_data['payment_due_date'] = form_data['payment_due_date'].isoformat()
            
            request.session['invoice_items'] = items_data
            request.session['invoice_form_data'] = form_data
            
            return redirect('entrepreneurs:preview_invoice')
    else:
        form = InvoiceGenerationForm(initial={
            'date': datetime.now().date(),
            'payment_due_date': datetime.now().date()
        })
        formset = InvoiceItemFormSet()
    
    return render(request, 'entrepreneurs/create_invoice.html', {
        'form': form,
        'formset': formset,
        'entrepreneur': entrepreneur
    })

@login_required
def preview_invoice(request):
    if 'invoice_items' not in request.session or 'invoice_form_data' not in request.session:
        return redirect('entrepreneurs:create_invoice')
    
    entrepreneur = get_object_or_404(EntrepreneurProfile, user=request.user)
    bank_details = get_object_or_404(BankDetails, entrepreneur=entrepreneur)
    
    # Восстанавливаем данные из сессии
    items_data = request.session['invoice_items']
    form_data = request.session['invoice_form_data'].copy()
    
    # Преобразуем строки обратно в даты
    from datetime import datetime
    form_data['date'] = datetime.strptime(form_data['date'], '%Y-%m-%d').date()
    form_data['payment_due_date'] = datetime.strptime(form_data['payment_due_date'], '%Y-%m-%d').date()
    
    # Создаем временные объекты InvoiceItem
    items = []
    for item_data in items_data:
        item = InvoiceItem(
            description=item_data['description'],
            quantity=item_data['quantity'],
            unit=item_data['unit'],
            price=item_data['price'],
            vat_rate=item_data['vat_rate']
        )
        items.append(item)
    
    if request.method == 'POST' and 'generate' in request.POST:
        file_stream = generate_invoice(entrepreneur, bank_details, items, form_data)
        
        doc = GeneratedDocument.objects.create(
            entrepreneur=entrepreneur,
            document_type='Счёт на оплату',
        )
        doc.file.save(f'Счет_{entrepreneur.inn}_{datetime.now().strftime("%Y%m%d%H%M%S")}.docx', file_stream)
        doc.save()
        
        del request.session['invoice_items']
        del request.session['invoice_form_data']
        
        messages.success(request, 'Документ успешно сгенерирован!')
        return redirect('entrepreneurs:document_detail', pk=doc.pk)
    
    return render(request, 'entrepreneurs/preview_invoice.html', {
        'entrepreneur': entrepreneur,
        'bank_details': bank_details,
        'items': items,
        'form_data': form_data
    })

@login_required
def document_detail(request, pk):
    document = get_object_or_404(GeneratedDocument, pk=pk, entrepreneur__user=request.user)
    return render(request, 'entrepreneurs/document_detail.html', {
        'document': document
    })

@login_required
def download_document(request, pk):
    document = get_object_or_404(GeneratedDocument, pk=pk, entrepreneur__user=request.user)
    response = FileResponse(document.file.open('rb'), as_attachment=True)
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(document.file.name)}"'
    return response

@login_required
def documents_list(request):
    entrepreneur = get_object_or_404(EntrepreneurProfile, user=request.user)
    documents = GeneratedDocument.objects.filter(entrepreneur=entrepreneur).order_by('-created_at')
    return render(request, 'entrepreneurs/documents_list.html', {
        'documents': documents
    })