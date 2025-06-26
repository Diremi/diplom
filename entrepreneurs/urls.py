from django.urls import path
from . import views

app_name = 'entrepreneurs'

urlpatterns = [
    path('', views.home_page, name='home'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.register_entrepreneur, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('documents/', views.documents_list, name='documents'),
    path('documents/bank/', views.bank_details, name='bank_details'),
    path('documents/invoice/', views.create_invoice, name='create_invoice'),
    path('documents/invoice/preview/', views.preview_invoice, name='preview_invoice'),
    path('documents/<int:pk>/', views.document_detail, name='document_detail'),
    path('documents/<int:pk>/download/', views.download_document, name='download_document'),
]