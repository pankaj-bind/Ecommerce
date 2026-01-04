from django.core.mail import send_mail
from django.conf import settings


def send_account_activation_email(email, email_token):
    subject = "Your account needs to be verified"
    email_from = settings.DEFAULT_FROM_EMAIL
    message = f'Hi, please verify your account.\nClick on the link to activate your account http://127.0.0.1:8000/accounts/activate/{email_token}'    
    send_mail(subject, message, email_from, [email])


def send_otp_email(email, otp, first_name):
    subject = "BuyNest - Verify Your Email"
    email_from = settings.DEFAULT_FROM_EMAIL
    message = f'''Hello {first_name},

Thank you for registering with BuyNest!

Your OTP for email verification is: {otp}

This OTP is valid for 10 minutes. Please do not share this code with anyone.

If you didn't request this, please ignore this email.

Best regards,
BuyNest Team'''
    send_mail(subject, message, email_from, [email])
