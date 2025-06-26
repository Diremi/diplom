from django.contrib import admin
from .models import EntrepreneurProfile

@admin.register(EntrepreneurProfile)
class EntrepreneurProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'inn', 'user', 'is_verified')
    search_fields = ('company_name', 'inn', 'ogrnip')
    list_filter = ('is_verified',)