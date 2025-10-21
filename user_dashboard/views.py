from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json
from .models import DashboardWidget

@login_required
@require_POST
def save_dashboard_layout(request):
    """
    Save the layout and visibility of dashboard widgets for the logged-in user.
    Expects a JSON payload with a list of widgets, each containing 'type' and 'order'.
    """
    try:
        data = json.loads(request.body)
        widget_layout = data.get('widgets', [])

        # Get all existing widgets for the user to update them
        existing_widgets = {w.widget_type: w for w in request.user.dashboard_widgets.all()}
        
        # A set to track which widgets are included in the new layout
        widgets_in_layout = set()

        for index, widget_data in enumerate(widget_layout):
            widget_type = widget_data.get('type')
            if not widget_type:
                continue

            widgets_in_layout.add(widget_type)
            
            # Update existing widget or create a new one
            widget, created = DashboardWidget.objects.get_or_create(
                user=request.user,
                widget_type=widget_type,
                defaults={'order': index, 'is_visible': True}
            )

            if not created:
                widget.order = index
                widget.is_visible = True
                widget.save()

        # Hide any widgets that were not in the new layout
        for widget_type, widget in existing_widgets.items():
            if widget_type not in widgets_in_layout:
                widget.is_visible = False
                widget.save()

        return JsonResponse({'status': 'success', 'message': 'Dashboard layout saved successfully.'})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

