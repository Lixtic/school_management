from django.contrib import admin
from django_tenants.admin import TenantAdminMixin

from tenants.models import School, Domain

@admin.register(School)
class SchoolAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'schema_name', 'created_on', 'on_trial', 'is_active')

@admin.register(Domain)
class DomainAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('domain', 'tenant', 'is_primary')
