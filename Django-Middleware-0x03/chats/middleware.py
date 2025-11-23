from datetime import datetime
import logging

from django.http import HttpResponseForbidden

class RolepermissionMiddleware:
    """
    Middleware that allows only users with role 'admin' or 'moderator'
    to access specific chat actions.
    """

    ALLOWED_ROLES = ['admin', 'moderator']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip check if user is anonymous
        if not request.user.is_authenticated:
            return HttpResponseForbidden("You must be logged in.")

        # Assume user has a 'role' attribute (admin, moderator, user)
        user_role = getattr(request.user, 'role', 'user')

        if user_role not in self.ALLOWED_ROLES:
            return HttpResponseForbidden("You do not have permission to perform this action.")

        return self.get_response(request)

class RequestLoggingMiddleware:
    """
    Middleware that logs every request with timestamp, user, and request path.
    """

    def __init__(self, get_response):
        self.get_response = get_response

        # Configure logger (writes to requests.log)
        logging.basicConfig(
            filename='requests.log',
            level=logging.INFO,
            format='%(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"

        # Log the request
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        self.logger.info(log_message)

        # Continue the request
        response = self.get_response(request)
        return response

from datetime import datetime
from django.http import HttpResponseForbidden

class RestrictAccessByTimeMiddleware:
    """
    Blocks access to the chat outside allowed hours (6 PM – 9 PM)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        now = datetime.now().time()

        # Allowed hours: 6 PM (18:00) to 9 PM (21:00)
        from datetime import time
        start_time = time(18, 0)   # 6 PM
        end_time = time(21, 0)     # 9 PM

        if not (start_time <= now <= end_time):
            return HttpResponseForbidden("Access to chat is restricted at this time.")

        return self.get_response(request)

from django.http import HttpResponseForbidden
from datetime import datetime, timedelta

class OffensiveLanguageMiddleware:
    """
    Middleware that limits the number of chat messages a user can send
    per IP address within a time window (e.g., 5 messages per minute).
    """

    # Class-level dictionary to track IP addresses and timestamps
    ip_message_tracker = {}

    MAX_MESSAGES = 5
    TIME_WINDOW = timedelta(minutes=1)

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only track POST requests (sending messages)
        if request.method == "POST" and request.path.startswith("/chats/messages/"):
            ip = self.get_client_ip(request)
            now = datetime.now()

            # Initialize tracker for this IP
            if ip not in self.ip_message_tracker:
                self.ip_message_tracker[ip] = []

            # Remove timestamps older than TIME_WINDOW
            self.ip_message_tracker[ip] = [
                t for t in self.ip_message_tracker[ip] if now - t < self.TIME_WINDOW
            ]

            if len(self.ip_message_tracker[ip]) >= self.MAX_MESSAGES:
                return HttpResponseForbidden("Message limit exceeded. Try again later.")

            # Record current message timestamp
            self.ip_message_tracker[ip].append(now)

        return self.get_response(request)

    def get_client_ip(self, request):
        # Get IP address from request headers
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
