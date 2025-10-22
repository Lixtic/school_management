from django.contrib import admin
from .models import Message
from schools.admin_mixins import SchoolFieldAdminMixin

@admin.register(Message)
class MessageAdmin(SchoolFieldAdminMixin, admin.ModelAdmin):
    list_display = ['subject', 'sender', 'recipient', 'sent_at', 'is_read']
    list_filter = ['is_read', 'sent_at', 'read_at']
    search_fields = ['subject', 'sender__username', 'recipient__username']
    readonly_fields = ['sent_at', 'read_at']
    date_hierarchy = 'sent_at'
    
    fieldsets = (
        ('Message', {
            'fields': ('subject', 'body')
        }),
        ('Participants', {
            'fields': ('sender', 'recipient')
        }),
        ('Status', {
            'fields': ('is_read', 'sent_at', 'read_at')
        }),
    )
