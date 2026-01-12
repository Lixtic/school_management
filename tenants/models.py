from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

class School(TenantMixin):
    name = models.CharField(max_length=100)
    created_on = models.DateField(auto_now_add=True)
    on_trial = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Default true, schema will be automatically created and synced when it is saved
    auto_create_schema = True

    def __str__(self):
        return self.name

class Domain(DomainMixin):
    pass
