from django.shortcuts import render, redirect
from .forms import UserForm
from vendor.forms import VendorForm
from .models import User, UserProfile
from django.contrib import messages
from vendor.models import Vendor


# Create your views here.
def registerUser(request):
    if request.method == "POST":
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

            messages.success(request, "Your account has been registered successfully")
            return redirect("accounts:registerUser")

    else:
        form = UserForm()

    context = {
        "form": form,
    }
    return render(request, "accounts/registerUser.html", context)


def registerVendor(request):
    if request.method == "POST":
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
            vendor.user_profile = UserProfile.objects.get(user=user)
            vendor.save()
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
