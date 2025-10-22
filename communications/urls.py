from django.urls import path
from . import views

app_name = 'communications'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('message/<int:message_id>/', views.view_message, name='view_message'),
    path('compose/', views.compose_message, name='compose_message'),
    path('compose/<int:recipient_id>/', views.compose_message, name='compose_to_recipient'),
]
