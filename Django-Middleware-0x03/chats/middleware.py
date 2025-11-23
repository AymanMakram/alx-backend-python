from datetime import datetime
import os
from django.conf import settings

class RequestLoggingMiddleware:
    """
    Middleware that logs each incoming request to a file.

    Logged format:
      "{datetime.now()} - User: {user} - Path: {request.path}"
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Use optional setting REQUESTS_LOG_PATH, fall back to BASE_DIR/requests.log
        base = getattr(settings, 'BASE_DIR', '.')
        self.log_path = getattr(settings, 'REQUESTS_LOG_PATH', os.path.join(str(base), 'requests.log'))

    def __call__(self, request):
        # Determine a friendly user representation
        user = getattr(request, 'user', None)
        if user is None:
            user_repr = 'Ayman'
        else:
            try:
                # If Django user-like object exists
                if getattr(user, 'is_authenticated', False):
                    user_repr = getattr(user, 'username', str(user))
                else:
                    user_repr = 'Ayman'
            except Exception:
                user_repr = str(user)

        # Compose log line
        line = f"{datetime.now()} - User: {user_repr} - Path: {request.path}\n"

        # Safely append to the log file; do not raise on errors to avoid breaking requests
        try:
            os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
            with open(self.log_path, 'a', encoding='utf-8') as fh:
                fh.write(line)
        except Exception:
            # Silently ignore logging failures (could be extended to use Django's logger)
            pass

        # Continue processing the request
        response = self.get_response(request)
        return response