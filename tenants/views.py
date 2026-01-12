from django.shortcuts import render, redirect
from django.db import transaction, connection
from .forms import SchoolSignupForm
from .models import School, Domain
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.conf import settings

def school_signup(request):
    if request.method == 'POST':
        form = SchoolSignupForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['school_name']
            schema_name = form.cleaned_data['schema_name']
            email = form.cleaned_data['email']
            
            try:
                with transaction.atomic():
                    # 1. Create Tenant
                    tenant = School(schema_name=schema_name, name=name, on_trial=True, is_active=True)
                    tenant.save()
                    
                    # 2. Create Domain (required for routing)
                    # For path-strategy, we normally dummy this or reuse localhost with different schema? 
                    # TenantSyncRouter usually needs a domain entry.
                    # We will create a pseudo-domain 'school.localhost' just to satisfy the model constraints
                    # even if we use path-routing.
                    
                    domain = Domain()
                    # In production we might not use this field for routing, but DB needs it
                    domain.domain = f"{schema_name}.local" 
                    domain.tenant = tenant
                    domain.is_primary = True
                    domain.save()
                    
                    # 3. Create Admin User (Switch to new schema)
                    connection.set_tenant(tenant)
                    User = get_user_model()
                    user = User.objects.create_superuser(
                        username='admin',
                        email=email,
                        password='admin', # Hardcoded for now, user should change
                        user_type='admin'
                    )
                    
                    # Switch back
                    public_schema = getattr(settings, 'PUBLIC_SCHEMA_NAME', 'public')
                    try:
                        public = School.objects.get(schema_name=public_schema)
                        connection.set_tenant(public)
                    except:
                        connection.set_schema_to_public()

                    messages.success(request, f"School '{name}' created successfully! Your login URL is /{schema_name}/login/")
                    return render(request, 'tenants/signup_success.html', {'schema_name': schema_name})
                    
            except Exception as e:
                # Switch back on error
                connection.set_schema_to_public()
                messages.error(request, f"Error creating school: {e}")
                
    else:
        form = SchoolSignupForm()
    
    return render(request, 'tenants/signup.html', {'form': form})
