from .models import SchoolInfo

def school_info(request):
    try:
        info = SchoolInfo.objects.first()
    except:
        info = None
        
    if not info:
        # Return defaults if no DB entry yet
        return {
            'school_name': "Daboya Girls Model JHS",
            'school_address': "P.O. Box 6, Daboya, North Gonja District",
            'school_motto': "Success, Our Concern",
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
