from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.models import User

@login_required
def delete_user(request):
    """
    Delete the current user's account and log them out.
    """
    user = request.user
    logout(request)  # End session before deleting account
    user.delete()    # Triggers post_delete signal
    return redirect('/')
