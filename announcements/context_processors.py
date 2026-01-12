def user_notifications(request):
    if request.user.is_authenticated:
        # Assuming related_name='notifications' in the Notification model
        # We fetch unread notifications
        return {
            'unread_notifications': request.user.notifications.filter(is_read=False).order_by('-created_at')[:5],
            'unread_count': request.user.notifications.filter(is_read=False).count()
        }
    return {}
