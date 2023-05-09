from django.core.exceptions import PermissionDenied
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, message
from django.conf import settings


def detectUser(user):
    if user.role == 1:
        redirectUrl = "accounts:vendorDashboard"
    elif user.role == 2:
        redirectUrl = "accounts:custDashboard"
    elif user.role == None and user.is_superadmin:
        redirectUrl = "/admin"
    return redirectUrl


def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied


def send_verification_email(request, user, mail_subject, email_template):
    from_email = settings.DEFAULT_FROM_EMAIL
    current_site = get_current_site(request)
    message = render_to_string(
        email_template,
        {
            "user": user,
            "domain": current_site,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": default_token_generator.make_token(user),
        },
    )
    # print("current_site", current_site, "message:", message)
    to_email = user.email
    mail = EmailMessage(mail_subject, message, from_email, to=[to_email])
    # print("mail", mail)
    mail.send()
