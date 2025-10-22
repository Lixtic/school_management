# API Enhancement Recommendations

## Add Django REST Framework

### 1. Install DRF
```bash
pip install djangorestframework djangorestframework-simplejwt
```

### 2. Add to requirements.txt
```
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.1
django-filter==23.5
drf-yasg==1.21.7  # For API documentation
```

### 3. Update settings.py
```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    'drf_yasg',  # Swagger/OpenAPI docs
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}
```

### 4. Create API structure
```
students/
    api/
        __init__.py
        serializers.py
        views.py
        permissions.py
        urls.py
```

### 5. Example serializer (students/api/serializers.py)
```python
from rest_framework import serializers
from students.models import Student, Grade

class StudentSerializer(serializers.ModelSerializer):
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    current_class_name = serializers.CharField(source='current_class.name', read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'admission_number', 'user_full_name', 
            'date_of_birth', 'gender', 'current_class_name',
            'roll_number', 'emergency_contact'
        ]
        read_only_fields = ['id']
    
    def validate(self, data):
        # Ensure student belongs to request user's school
        request = self.context.get('request')
        if request and hasattr(request.user, 'school'):
            data['school'] = request.user.school
        return data

class GradeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    
    class Meta:
        model = Grade
        fields = [
            'id', 'student', 'student_name', 'subject', 'subject_name',
            'term', 'class_score', 'exams_score', 'total_score',
            'grade', 'remarks', 'subject_position'
        ]
        read_only_fields = ['id', 'total_score', 'grade', 'remarks', 'subject_position']
```

### 6. Example ViewSet (students/api/views.py)
```python
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from students.models import Student, Grade
from .serializers import StudentSerializer, GradeSerializer
from .permissions import IsSchoolMember

class StudentViewSet(viewsets.ModelViewSet):
    serializer_class = StudentSerializer
    permission_classes = [IsSchoolMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['gender', 'current_class']
    search_fields = ['user__first_name', 'user__last_name', 'admission_number']
    ordering_fields = ['date_of_admission', 'user__last_name']
    
    def get_queryset(self):
        # Automatic school filtering
        queryset = Student.objects.select_related('user', 'current_class')
        
        if self.request.user.is_superuser:
            return queryset
        
        return queryset.filter(school=self.request.user.school)
    
    @action(detail=True, methods=['get'])
    def grades(self, request, pk=None):
        """Get all grades for a specific student"""
        student = self.get_object()
        grades = Grade.objects.filter(student=student).select_related('subject', 'academic_year')
        serializer = GradeSerializer(grades, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def attendance(self, request, pk=None):
        """Get attendance records for a specific student"""
        student = self.get_object()
        # Implement attendance retrieval
        return Response({'message': 'Attendance records'})
```

### 7. Custom permissions (students/api/permissions.py)
```python
from rest_framework import permissions

class IsSchoolMember(permissions.BasePermission):
    """
    Permission that ensures users can only access resources from their own school
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or hasattr(request.user, 'school')
        )
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        if hasattr(obj, 'school'):
            return obj.school == request.user.school
        
        return False

class IsTeacherOrAdmin(permissions.BasePermission):
    """Allow teachers and admins only"""
    def has_permission(self, request, view):
        return request.user.user_type in ['teacher', 'admin'] or request.user.is_superuser
```

### 8. URL configuration (students/api/urls.py)
```python
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')

urlpatterns = router.urls
```

### 9. Main API URLs (school_system/urls.py)
```python
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="School Management API",
        default_version='v1',
        description="API for Asetena School Management System",
    ),
    public=True,
)

urlpatterns = [
    # ... existing URLs ...
    
    # API Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='api-docs'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='api-redoc'),
    
    # API Endpoints
    path('api/v1/', include('students.api.urls')),
    path('api/v1/', include('teachers.api.urls')),
    path('api/v1/', include('academics.api.urls')),
]
```

### Benefits:
- Mobile app support (iOS/Android)
- Third-party integrations
- JavaScript frontend frameworks (React, Vue)
- Automated API documentation
- Better separation of concerns
- Token-based authentication
