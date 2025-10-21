document.addEventListener('DOMContentLoaded', function () {
    const dashboardContainer = document.querySelector('.dashboard-grid');
    if (!dashboardContainer) return;

    // Initialize SortableJS for drag-and-drop
    const sortable = new Sortable(dashboardContainer, {
        animation: 150,
        handle: '.drag-handle', // Use a handle to drag widgets
        ghostClass: 'widget-ghost',
        chosenClass: 'widget-chosen',
        dragClass: 'widget-dragging',
        onEnd: saveLayout,
    });

    // Function to save the new layout
    function saveLayout() {
        const widgets = [];
        dashboardContainer.querySelectorAll('.dashboard-widget').forEach((widget, index) => {
            widgets.push({
                type: widget.dataset.widgetType,
                order: index,
            });
        });

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch('/dashboard-settings/save-layout/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify({ widgets: widgets }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                console.log('Dashboard layout saved.');
                // Optionally, show a success toast
                if (window.showToast) {
                    window.showToast('Dashboard layout updated!', 'success');
                }
            } else {
                console.error('Failed to save dashboard layout:', data.message);
                if (window.showToast) {
                    window.showToast(`Error: ${data.message}`, 'error');
                }
            }
        })
        .catch(error => {
            console.error('Error saving dashboard layout:', error);
            if (window.showToast) {
                window.showToast('A network error occurred.', 'error');
            }
        });
    }
});
