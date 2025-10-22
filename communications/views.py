from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Message
from .forms import MessageForm
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def inbox(request):
    user = request.user
    received_messages = Message.objects.filter(recipient=user).order_by('-sent_at')
    return render(request, 'communications/inbox.html', {'messages': received_messages})

@login_required
def view_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    
    # Check if the user is either the sender or recipient
    if request.user != message.sender and request.user != message.recipient:
        messages.error(request, "You do not have permission to view this message.")
        return redirect('messages:inbox')

    if message.recipient == request.user and not message.is_read:
        message.is_read = True
        message.read_at = timezone.now()
        message.save()
        
    return render(request, 'communications/view_message.html', {'message': message})

@login_required
def compose_message(request, recipient_id=None):
    if request.method == 'POST':
        form = MessageForm(request.POST, user=request.user)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            messages.success(request, "Message sent successfully!")
            return redirect('messages:inbox')
    else:
        initial_data = {}
        if recipient_id:
            try:
                recipient = User.objects.get(id=recipient_id)
                initial_data['recipient'] = recipient
            except User.DoesNotExist:
                messages.error(request, "The recipient you are trying to message does not exist.")
        
        form = MessageForm(initial=initial_data, user=request.user)
        
    return render(request, 'communications/compose_message.html', {'form': form})
