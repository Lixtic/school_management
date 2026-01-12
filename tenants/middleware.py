from django.conf import settings
from django.db import connection
from django.http import Http404
from django.urls import set_urlconf
from django_tenants.middleware.main import TenantMainMiddleware
from tenants.models import School

class TenantPathMiddleware(TenantMainMiddleware):
    def process_request(self, request):
        # 1. Start with Public context to be safe
        connection.set_schema_to_public()
        
        # 2. Inspect Path
        path_parts = request.path.strip('/').split('/')
        possible_schema = path_parts[0] if path_parts else None
        
        tenant = None

        # 3. Check if the first segment matches a valid School schema (excluding 'public')
        if possible_schema and possible_schema != 'public' and possible_schema not in ['static', 'media', 'admin', 'accounts']:
            # Try to find the school
            tenant = School.objects.filter(schema_name=possible_schema).first()
        
        if tenant:
            # === TENANT FOUND ===
            request.tenant = tenant
            connection.set_tenant(request.tenant)
            
            # Setup URL Routing for Tenant Apps
            # This points to the standard urls.py which routes to academics, students, etc.
            # IMPT: We are NOT stripping the prefix here because it messes up 'reverse()' 
            # and form actions unless we use complex SCRIPT_NAME hacks.
            # Instead, we will prefix the tenant URLs in the main urls.py?
            # 
            # Wait, if we don't strip it, the tenant's urls.py needs to expect 'school1/dashboard/'
            # That is impossible to maintain dynamically.
            #
            # The standard Django way for sub-path apps is modifying SCRIPT_NAME.
            # request.META['SCRIPT_NAME'] = '/' + possible_schema
            # request.META['PATH_INFO'] = request.path[len(possible_schema)+1:] 
            
            # Let's try the SCRIPT_NAME approach.
            # Original: /school1/dashboard/
            # SCRIPT_NAME: /school1
            # PATH_INFO: /dashboard/
            
            script_prefix = f"/{possible_schema}"
            if request.path.startswith(script_prefix):
                request.path_info = request.path[len(script_prefix):]
                # If path was exactly '/school1', path_info is empty, should be '/'
                if not request.path_info:
                    request.path_info = '/'
                
                request.META['SCRIPT_NAME'] = script_prefix
            
            self.setup_url_routing(request)
            
        else:
            # === PUBLIC CONTEXT ===
            # No tenant found in path -> Serve Public Site
            try:
                public_schema = settings.PUBLIC_SCHEMA_NAME
                request.tenant = School.objects.get(schema_name=public_schema)
            except School.DoesNotExist:
                # Fallback if DB is empty
                raise Http404("Public tenant not found")
                
            connection.set_tenant(request.tenant)
            self.setup_url_routing(request)
