import os
import sys
import django
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_system.settings')
django.setup()

def debug_email():
    print("="*50)
    print("EMAIL CONFIGURATION DEBUGGER")
    print("="*50)
    
    # 1. Check Settings
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    
    # Mask password
    pwd = settings.EMAIL_HOST_PASSWORD
    print(f"EMAIL_HOST_PASSWORD: {'*' * len(pwd) if pwd else 'NOT SET'}")

    # 2. Check Users
    User = get_user_model()
    print("\n" + "="*50)
    print("REGISTERED USERS")
    print("="*50)
    users = User.objects.all()
    if not users.exists():
        print("No users found in database!")
    else:
        for u in users:
            print(f"- {u.username} (Type: {u.user_type}): {u.email}")

    # 3. Test Sending
    print("\n" + "="*50)
    print("SENDING TEST EMAIL")
    print("="*50)
    
    if not settings.EMAIL_HOST_USER:
        print("ERROR: EMAIL_HOST_USER is not set. Cannot send email.")
        return

    recipient = input("Enter an email address to send a test to: ").strip()
    if not recipient:
        print("Skipping test email.")
        return

    try:
        print(f"Attempting to send to {recipient}...")
        send_mail(
            subject='School System Email Test',
            message='If you are reading this, your email configuration is working correctly.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
        print("SUCCESS! Email sent successfully.")
    except Exception as e:
        print(f"FAILURE! Could not send email.")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")

if __name__ == "__main__":
    debug_email()
