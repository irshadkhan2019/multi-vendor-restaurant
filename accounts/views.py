from django.shortcuts import render, redirect
from .forms import UserForm
from .models import User
from django.contrib import messages


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
