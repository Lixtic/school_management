/**
 * Form Validation and Enhancement System
 * Provides real-time validation, inline feedback, and better UX for forms
 */

class FormValidator {
    constructor(formElement) {
        this.form = formElement;
        this.fields = {};
        this.init();
    }

    init() {
        // Add validation to all inputs
        const inputs = this.form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            this.setupField(input);
        });

        // Handle form submission
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    setupField(input) {
        const fieldName = input.name || input.id;
        if (!fieldName) return;

        this.fields[fieldName] = {
            element: input,
            valid: true,
            touched: false
        };

        // Add validation on blur
        input.addEventListener('blur', () => {
            this.fields[fieldName].touched = true;
            this.validateField(input);
        });

        // Add real-time validation on input (with debounce)
        let timeout;
        input.addEventListener('input', () => {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                if (this.fields[fieldName].touched) {
                    this.validateField(input);
                }
            }, 500);
        });

        // Add required indicator
        if (input.hasAttribute('required')) {
            this.addRequiredIndicator(input);
        }

        // Add password strength meter if password field
        if (input.type === 'password' && input.id === 'id_password1') {
            this.addPasswordStrengthMeter(input);
        }
    }

    validateField(input) {
        const value = input.value.trim();
        let isValid = true;
        let errorMessage = '';

        // Required validation
        if (input.hasAttribute('required') && !value) {
            isValid = false;
            errorMessage = 'This field is required';
        }

        // Email validation
        if (input.type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Please enter a valid email address';
            }
        }

        // Phone validation
        if (input.type === 'tel' && value) {
            const phoneRegex = /^[\d\s\-\+\(\)]+$/;
            if (!phoneRegex.test(value) || value.replace(/\D/g, '').length < 10) {
                isValid = false;
                errorMessage = 'Please enter a valid phone number';
            }
        }

        // Min length validation
        if (input.hasAttribute('minlength') && value) {
            const minLength = parseInt(input.getAttribute('minlength'));
            if (value.length < minLength) {
                isValid = false;
                errorMessage = `Must be at least ${minLength} characters`;
            }
        }

        // Max length validation
        if (input.hasAttribute('maxlength') && value) {
            const maxLength = parseInt(input.getAttribute('maxlength'));
            if (value.length > maxLength) {
                isValid = false;
                errorMessage = `Must not exceed ${maxLength} characters`;
            }
        }

        // Pattern validation
        if (input.hasAttribute('pattern') && value) {
            const pattern = new RegExp(input.getAttribute('pattern'));
            if (!pattern.test(value)) {
                isValid = false;
                errorMessage = input.getAttribute('title') || 'Invalid format';
            }
        }

        // Number validations
        if (input.type === 'number' && value) {
            const num = parseFloat(value);
            
            if (input.hasAttribute('min') && num < parseFloat(input.getAttribute('min'))) {
                isValid = false;
                errorMessage = `Must be at least ${input.getAttribute('min')}`;
            }
            
            if (input.hasAttribute('max') && num > parseFloat(input.getAttribute('max'))) {
                isValid = false;
                errorMessage = `Must not exceed ${input.getAttribute('max')}`;
            }
        }

        // Password confirmation
        if (input.id === 'id_password2') {
            const password1 = this.form.querySelector('#id_password1');
            if (password1 && value !== password1.value) {
                isValid = false;
                errorMessage = 'Passwords do not match';
            }
        }

        // Update field status
        this.updateFieldStatus(input, isValid, errorMessage);
        this.fields[input.name || input.id].valid = isValid;

        return isValid;
    }

    updateFieldStatus(input, isValid, errorMessage) {
        const formGroup = input.closest('.mb-3') || input.closest('.form-group') || input.parentElement;
        
        // Remove existing feedback
        const existingFeedback = formGroup.querySelector('.invalid-feedback, .valid-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }

        // Remove validation classes
        input.classList.remove('is-valid', 'is-invalid');

        // Add appropriate class and feedback
        if (this.fields[input.name || input.id].touched) {
            if (isValid && input.value.trim()) {
                input.classList.add('is-valid');
                const feedback = document.createElement('div');
                feedback.className = 'valid-feedback';
                feedback.style.display = 'block';
                feedback.innerHTML = '<i class="bi bi-check-circle-fill me-1"></i>Looks good!';
                formGroup.appendChild(feedback);
            } else if (!isValid) {
                input.classList.add('is-invalid');
                const feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                feedback.style.display = 'block';
                feedback.innerHTML = `<i class="bi bi-exclamation-circle-fill me-1"></i>${errorMessage}`;
                formGroup.appendChild(feedback);
            }
        }
    }

    addRequiredIndicator(input) {
        const label = this.form.querySelector(`label[for="${input.id}"]`);
        if (label && !label.querySelector('.required-indicator')) {
            const indicator = document.createElement('span');
            indicator.className = 'required-indicator';
            indicator.innerHTML = ' <span style="color: #e74c3c;">*</span>';
            indicator.title = 'Required field';
            label.appendChild(indicator);
        }
    }

    addPasswordStrengthMeter(input) {
        const formGroup = input.closest('.mb-3') || input.closest('.form-group') || input.parentElement;
        
        const meterHtml = `
            <div class="password-strength-meter mt-2">
                <div class="strength-bar">
                    <div class="strength-bar-fill" id="strengthBarFill"></div>
                </div>
                <div class="strength-text" id="strengthText">
                    <small class="text-muted">Password strength: <span id="strengthLabel">Not entered</span></small>
                </div>
                <div class="strength-hints mt-2">
                    <small class="text-muted">
                        <i class="bi bi-info-circle"></i> Use at least 8 characters with uppercase, lowercase, numbers, and symbols
                    </small>
                </div>
            </div>
        `;
        
        formGroup.insertAdjacentHTML('beforeend', meterHtml);

        input.addEventListener('input', () => {
            const password = input.value;
            const strength = this.calculatePasswordStrength(password);
            this.updatePasswordStrengthMeter(strength);
        });
    }

    calculatePasswordStrength(password) {
        let strength = 0;
        
        if (password.length >= 8) strength += 25;
        if (password.length >= 12) strength += 25;
        if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength += 20;
        if (/\d/.test(password)) strength += 15;
        if (/[^a-zA-Z\d]/.test(password)) strength += 15;
        
        return Math.min(strength, 100);
    }

    updatePasswordStrengthMeter(strength) {
        const fill = document.getElementById('strengthBarFill');
        const label = document.getElementById('strengthLabel');
        
        if (!fill || !label) return;

        fill.style.width = strength + '%';
        
        let color, text;
        if (strength < 25) {
            color = '#e74c3c';
            text = 'Weak';
        } else if (strength < 50) {
            color = '#f39c12';
            text = 'Fair';
        } else if (strength < 75) {
            color = '#3498db';
            text = 'Good';
        } else {
            color = '#27ae60';
            text = 'Strong';
        }
        
        fill.style.backgroundColor = color;
        label.textContent = text;
        label.style.color = color;
        label.style.fontWeight = '600';
    }

    handleSubmit(e) {
        let isValid = true;

        // Validate all fields
        Object.keys(this.fields).forEach(fieldName => {
            const field = this.fields[fieldName];
            field.touched = true;
            if (!this.validateField(field.element)) {
                isValid = false;
            }
        });

        if (!isValid) {
            e.preventDefault();
            
            // Scroll to first error
            const firstInvalid = this.form.querySelector('.is-invalid');
            if (firstInvalid) {
                firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstInvalid.focus();
            }

            toast.error('Please correct the errors in the form');
            return false;
        }

        return true;
    }
}

// Auto-initialize forms
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form:not(.no-validation)');
    forms.forEach(form => {
        new FormValidator(form);
    });

    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Add helpful tooltips to common fields
document.addEventListener('DOMContentLoaded', function() {
    // Email fields
    document.querySelectorAll('input[type="email"]').forEach(input => {
        if (!input.hasAttribute('title')) {
            input.setAttribute('title', 'Enter a valid email address (e.g., user@example.com)');
            input.setAttribute('data-bs-toggle', 'tooltip');
            input.setAttribute('data-bs-placement', 'top');
        }
    });

    // Phone fields
    document.querySelectorAll('input[type="tel"]').forEach(input => {
        if (!input.hasAttribute('title')) {
            input.setAttribute('title', 'Enter a valid phone number with country code');
            input.setAttribute('data-bs-toggle', 'tooltip');
            input.setAttribute('data-bs-placement', 'top');
        }
    });

    // Date fields
    document.querySelectorAll('input[type="date"]').forEach(input => {
        if (!input.hasAttribute('title')) {
            input.setAttribute('title', 'Select a date from the calendar');
            input.setAttribute('data-bs-toggle', 'tooltip');
            input.setAttribute('data-bs-placement', 'top');
        }
    });
});
