# core/utils.py
import os
import secrets
from datetime import timedelta

from django.utils import timezone
from .models import OTPCode


# ======================
# OTP helpers
# ======================

def generate_otp(length: int = 6) -> str:
    """
    Generate a cryptographically secure numeric OTP of given length.
    Default: 6 digits.
    """
    if length < 4:
        length = 4
    # secrets.randbelow(10**length) gives 0..999999; zfill pads leading zeros
    return str(secrets.randbelow(10 ** length)).zfill(length)


def create_otp_for_user(user, length: int = 6) -> str:
    """
    Create & store a new OTP for the given user. Returns the OTP string.
    Note: Delivery (SMS/Email) should be handled by the caller.
    """
    otp = generate_otp(length=length)
    OTPCode.objects.create(user=user, code=otp)
    # For dev visibility; remove in prod:
    print(f"[DEBUG] OTP for {user.username}: {otp}")
    return otp


def verify_otp(user, code: str, expire_minutes: int | None = None) -> bool:
    """
    Verify if the given OTP is valid for the user.
    Marks the OTP as used on success.

    Args:
        user: Django User instance
        code: OTP string user submitted
        expire_minutes: optional expiry window. If None, reads from
                        env OTP_EXPIRE_MINUTES (default 10).
    """
    if not code:
        return False

    if expire_minutes is None:
        try:
            expire_minutes = int(os.getenv("OTP_EXPIRE_MINUTES", "10"))
        except ValueError:
            expire_minutes = 10

    try:
        # Latest unused OTP matching this code
        otp_qs = OTPCode.objects.filter(user=user, code=code, is_used=False)
        if expire_minutes > 0:
            cutoff = timezone.now() - timedelta(minutes=expire_minutes)
            otp_qs = otp_qs.filter(created_at__gte=cutoff)

        otp_obj = otp_qs.latest("created_at")  # relies on created_at field
    except OTPCode.DoesNotExist:
        return False

    otp_obj.is_used = True
    otp_obj.save(update_fields=["is_used"])
    return True


# ======================
# Response helpers
# ======================

def success_response(message: str, data: dict | None = None) -> dict:
    """
    Return a consistent success JSON structure (dict).
    Views can wrap this with JsonResponse.
    """
    return {
        "status": "success",
        "message": message,
        "data": data or {},
    }


def error_response(message: str, code: int = 400) -> dict:
    """
    Return a consistent error JSON structure (dict).
    Views can wrap this with JsonResponse(status=code).
    """
    return {
        "status": "error",
        "message": message,
        "code": code,
    }


# ======================
# Profile helpers
# ======================

def update_last_login(user) -> None:
    """
    Update the last login time on the user's StudentProfile (if present).
    """
    profile = getattr(user, "profile", None)
    if profile:
        profile.last_login_at = timezone.now()
        profile.save(update_fields=["last_login_at"])
