/**
 * Toast Notification System for Asetena Management System
 * Provides beautiful, dismissible toast notifications with multiple types
 */

class ToastNotification {
    constructor() {
        this.container = this.createContainer();
        this.toasts = [];
    }

    createContainer() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        return container;
    }

    show(message, type = 'info', duration = 5000) {
        const toast = this.createToast(message, type);
        this.container.appendChild(toast);
        this.toasts.push(toast);

        // Trigger animation
        setTimeout(() => toast.classList.add('show'), 10);

        // Auto dismiss
        if (duration > 0) {
            setTimeout(() => this.dismiss(toast), duration);
        }

        return toast;
    }

    createToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icons = {
            success: 'bi-check-circle-fill',
            error: 'bi-x-circle-fill',
            warning: 'bi-exclamation-triangle-fill',
            info: 'bi-info-circle-fill'
        };

        const colors = {
            success: '#27ae60',
            error: '#e74c3c',
            warning: '#f39c12',
            info: '#3498db'
        };

        toast.innerHTML = `
            <div class="toast-icon" style="background-color: ${colors[type]}">
                <i class="bi ${icons[type]}"></i>
            </div>
            <div class="toast-content">
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="toastManager.dismiss(this.parentElement)">
                <i class="bi bi-x"></i>
            </button>
        `;

        // Make toast dismissible on click
        toast.addEventListener('click', (e) => {
            if (!e.target.closest('.toast-close')) {
                this.dismiss(toast);
            }
        });

        return toast;
    }

    dismiss(toast) {
        if (typeof toast === 'string') {
            toast = document.querySelector(toast);
        }
        
        if (toast && toast.classList.contains('show')) {
            toast.classList.remove('show');
            toast.classList.add('hide');
            
            setTimeout(() => {
                if (toast.parentElement) {
                    toast.parentElement.removeChild(toast);
                }
                const index = this.toasts.indexOf(toast);
                if (index > -1) {
                    this.toasts.splice(index, 1);
                }
            }, 300);
        }
    }

    success(message, duration = 5000) {
        return this.show(message, 'success', duration);
    }

    error(message, duration = 7000) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration = 6000) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration = 5000) {
        return this.show(message, 'info', duration);
    }

    dismissAll() {
        this.toasts.forEach(toast => this.dismiss(toast));
    }
}

// Create global instance
const toastManager = new ToastNotification();

// Expose to window for easy access
window.toast = {
    success: (msg, duration) => toastManager.success(msg, duration),
    error: (msg, duration) => toastManager.error(msg, duration),
    warning: (msg, duration) => toastManager.warning(msg, duration),
    info: (msg, duration) => toastManager.info(msg, duration),
    dismissAll: () => toastManager.dismissAll()
};

// Auto-show Django messages as toasts
document.addEventListener('DOMContentLoaded', function() {
    // Convert Django messages to toasts
    const djangoMessages = document.querySelectorAll('.django-message');
    djangoMessages.forEach(msg => {
        const type = msg.dataset.type || 'info';
        const message = msg.textContent.trim();
        toast[type](message);
        msg.remove();
    });
});

// AJAX Error Handler
window.handleAjaxError = function(xhr, status, error) {
    let message = 'An error occurred. Please try again.';
    
    if (xhr.responseJSON && xhr.responseJSON.message) {
        message = xhr.responseJSON.message;
    } else if (xhr.responseText) {
        try {
            const response = JSON.parse(xhr.responseText);
            message = response.message || response.error || message;
        } catch (e) {
            message = xhr.statusText || message;
        }
    }
    
    toast.error(message);
};

// AJAX Success Handler
window.handleAjaxSuccess = function(response) {
    if (response && response.message) {
        toast.success(response.message);
    }
};
