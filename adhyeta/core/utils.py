import random
from django.utils import timezone
from .models import OTPCode


def generate_otp():
    """
    Generate a 6-digit random OTP as a string.
    """
    return str(random.randint(100000, 999999))


def create_otp_for_user(user):
    """
    Create a new OTP for a given user and save it in the database.
    """
    otp = generate_otp()
    OTPCode.objects.create(user=user, code=otp)
    print(f"[DEBUG] OTP for {user.username}: {otp}")  # Simulated sending (for dev)
    return otp


def verify_otp(user, code):
    """
    Verify if the given OTP is valid for the user.
    """
    try:
        otp_obj = OTPCode.objects.filter(user=user, code=code, is_used=False).latest('created_at')
        otp_obj.is_used = True
        otp_obj.save()
        return True
    except OTPCode.DoesNotExist:
        return False


def success_response(message, data=None):
    """
    Return a consistent success JSON structure.
    """
    return {
        "status": "success",
        "message": message,
        "data": data or {}
    }


def error_response(message, code=400):
    """
    Return a consistent error JSON structure.
    """
    return {
        "status": "error",
        "message": message,
        "code": code
    }


def update_last_login(user):
    """
    Update the last login time for the user's StudentProfile.
    """
    profile = getattr(user, "profile", None)
    if profile:
        profile.last_login_at = timezone.now()
        profile.save()
