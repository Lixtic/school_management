from django.db.utils import OperationalError, ProgrammingError

def user_notifications(request):
    if request.user.is_authenticated:
        try:
            # Assuming related_name='notifications' in the Notification model
            # We fetch unread notifications
            return {
                'unread_notifications': request.user.notifications.filter(is_read=False).order_by('-created_at')[:5],
                'unread_count': request.user.notifications.filter(is_read=False).count()
            }
        except (OperationalError, ProgrammingError):
            # This happens if the table doesn't exist yet (e.g. before migration)
            return {'unread_notifications': [], 'unread_count': 0}
            
    return {}
