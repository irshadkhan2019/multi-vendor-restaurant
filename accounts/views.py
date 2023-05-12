from django.shortcuts import render, redirect
from .forms import UserForm
from vendor.forms import VendorForm
from .models import User, UserProfile
from django.contrib import messages, auth
from vendor.models import Vendor
from django.contrib.auth.decorators import login_required, user_passes_test
from .utils import (
    detectUser,
    check_role_customer,
    check_role_vendor,
    send_verification_email,
)
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

from django.template.defaultfilters import slugify


# Create your views here.
def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in!")
        return redirect("accounts:myAccount")
    elif request.method == "POST":
        # print(request.POST)
        form = UserForm(request.POST)
        if form.is_valid():
            # user: User = form.save(commit=False)
            # # hash password
            # password = form.cleaned_data["password"]

            # # assign customer role to user
            # user.role = User.CUSTOMER
            # user.set_password(password)
            # user.save()

            # create user using create_user method
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user: User = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
            )
            user.role = User.CUSTOMER
            user.save()

            # send mail
            mail_subject = "Verify and Activate your account"
            email_template = "accounts/emails/account_verification_email.html"
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, "Your account has been registered successfully")
            return redirect("accounts:registerUser")

    else:
        form = UserForm()

    context = {
        "form": form,
    }
    return render(request, "accounts/registerUser.html", context)


def registerVendor(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in!")
        return redirect("accounts:myAccount")
    elif request.method == "POST":
        # print(request.POST)
        # print("FILES", request.FILES)
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
            )
            user.role = User.VENDOR
            user.save()

            vendor: Vendor = v_form.save(commit=False)
            vendor.user = user
            vendor_name = v_form.cleaned_data["vendor_name"]
            vendor.vendor_slug = slugify(vendor_name) + "-" + str(user.id)

            vendor.user_profile = UserProfile.objects.get(user=user)
            vendor.save()

            # send mail
            mail_subject = "Verify and Activate your account"
            email_template = "accounts/emails/account_verification_email.html"
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(
                request,
                "Your account has been registered sucessfully! Please wait for the approval.",
            )
            return redirect("accounts:registerVendor")
        else:
            print(form.errors)
            print("invalid form")
    else:
        form = UserForm()
        v_form = VendorForm()

    context = {
        "form": form,
        "v_form": v_form,
    }

    return render(request, "accounts/registerVendor.html", context)


def login(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in!")
        return redirect("accounts:myAccount")
    elif request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user: User = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, "You are now logged in.")
            # myAccount view dynamically route user to his respective dashboard based on his role
            return redirect("accounts:myAccount")
        else:
            messages.error(request, "Invalid login credentials")
            return redirect("accounts:login")
    return render(request, "accounts/login.html")


def logout(request):
    auth.logout(request)
    messages.info(request, "You are logged out.")
    return redirect("accounts:login")


# used to dynamically route user based on its role
@login_required(login_url="accounts:login")
def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    # print("Curent user is", user, "redirected to ", redirectUrl)
    return redirect(redirectUrl)


@login_required(login_url="accounts:login")
@user_passes_test(check_role_customer)
def custDashboard(request):
    return render(request, "accounts/custDashboard.html")


@login_required(login_url="accounts:login")
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    return render(request, "accounts/vendorDashboard.html")


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64)
        user: User = User._default_manager.get(pk=uid)
        # print(user.username, uid, redirect("accounts:myAccount"))
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulation! Your account is activated.")
        return redirect("accounts:myAccount")
    else:
        messages.error(request, "Invalid activation link")
        return redirect("accounts:myAccount")


def forgot_password(request):
    if request.method == "POST":
        email = request.POST["email"]

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # send reset password email
            mail_subject = "Reset Your Password"
            email_template = "accounts/emails/reset_password_email.html"
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(
                request, "Password reset link has been sent to your email address."
            )
            return redirect("accounts:login")
        else:
            messages.error(request, "Account does not exist")
            return redirect("accounts:forgot_password")
    return render(request, "accounts/forgot_password.html")


def reset_password_validate(request, uidb64, token):
    # validate the user by decoding the token and user pk
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
        # print("current userid", uid, user)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        # print("SESSION_:", dir(request.session))
        messages.info(request, "Please reset your password")
        return redirect("accounts:reset_password")
    else:
        messages.error(request, "This link has been expired!")
        return redirect("accounts:myAccount")


def reset_password(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password == confirm_password:
            pk = request.session.get("uid")
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, "Password reset successful")
            return redirect("accounts:login")
        else:
            messages.error(request, "Password do not match!")
            return redirect("accounts:reset_password")
    return render(request, "accounts/reset_password.html")
