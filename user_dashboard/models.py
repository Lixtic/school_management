from django.db import models
from django.conf import settings

class DashboardWidget(models.Model):
    """
    Represents a customizable widget on a user's dashboard.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dashboard_widgets')
    widget_type = models.CharField(max_length=50, help_text="Identifier for the widget type (e.g., 'summary_stats', 'recent_grades')")
    order = models.PositiveIntegerField(default=0, help_text="The display order of the widget on the dashboard.")
    is_visible = models.BooleanField(default=True, help_text="Whether the widget is visible to the user.")
    config = models.JSONField(default=dict, blank=True, help_text="Custom configuration for the widget (e.g., specific class for grades).")

    class Meta:
        ordering = ['user', 'order']
        unique_together = ('user', 'widget_type')

    def __str__(self):
        return f"{self.user.username}'s {self.widget_type} Widget (Order: {self.order})"

