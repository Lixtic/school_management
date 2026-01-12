from .models import SchoolInfo

def school_info(request):
    try:
        info = SchoolInfo.objects.first()
    except:
        info = None
        
    if not info:
        # Check if we are in a tenant context
        tenant_name = "School Portal"
        if hasattr(request, 'tenant') and request.tenant.schema_name != 'public':
            tenant_name = request.tenant.name

        # Return defaults if no DB entry yet
        return {
            'school_name': tenant_name,
            'school_address': "Address Not Set",
            'school_motto': "Knowledge is Power",
        }
        
    return {
        'school_name': info.name,
        'school_address': info.address,
        'school_phone': info.phone,
        'school_email': info.email,
        'school_motto': info.motto,
        'school_logo': info.logo,
        'school_object': info
    }
