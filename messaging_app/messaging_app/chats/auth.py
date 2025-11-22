from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication, BasicAuthentication


def get_authenticated_user(request):
    """
    Returns the authenticated user for the request.
    Works with Session auth (request.user) and JWT auth.
    Returns:
        user instance or None
    """
    user = getattr(request, "user", None)
    if user and getattr(user, "is_authenticated", False):
        return user

    # Try JWT authentication
    jwt_auth = JWTAuthentication()
    try:
        validated = jwt_auth.authenticate(request)
    except Exception:
        return None

    if validated:
        user_obj, token = validated
        return user_obj

    return None