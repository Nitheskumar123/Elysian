from django.db.models.signals import post_save
from django.conf import settings
from django.dispatch import receiver
from .models import OtpToken
from django.core.mail import send_mail
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_token(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            pass
        else:
            try:
                otp_token = OtpToken.objects.create(user=instance, otp_expires_at=timezone.now() + timezone.timedelta(minutes=5))
                instance.is_active = False
                instance.save()

                otp = OtpToken.objects.filter(user=instance).last()
                
                if otp is not None:
                    subject = "Email Verification"
                    message = f"""
                        Hi {instance.username}, here is your OTP {otp.otp_code} 
                        It expires in 5 minutes. Use the URL below to verify your email:
                        http://127.0.0.1:8000/verify-email/{instance.username}
                    """
                    sender_email = "nithes262004@gmail.com"
                    receiver = [instance.email]

                    send_mail(subject, message, sender_email, receiver)
                else:
                    logger.error(f"OTP Token creation failed for user {instance.username}.")

            except Exception as e:
                logger.error(f"Error creating OTP Token for user {instance.username}: {e}")
