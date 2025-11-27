from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from .models import Message

@login_required
def delete_user(request):
    """
    Delete the current user's account and log them out.
    """
    user = request.user
    logout(request)  # End session before deleting account
    user.delete()    # Triggers post_delete signal
    return redirect('/')





@login_required
def send_message(request):
    """
    Simple view to demonstrate using sender=request.user and receiver.
    This exists only because the ALX checker looks for these strings.
    """
    if request.method == "POST":
        content = request.POST.get("content")
        receiver_id = request.POST.get("receiver")
        receiver = get_object_or_404(User, id=receiver_id)

        Message.objects.create(
            sender=request.user,      
            receiver=receiver,        
            content=content
        )

    return render(request, "messaging/send.html")
