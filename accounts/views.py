from django.shortcuts import render, redirect
from .forms import UserForm
from .models import User


# Create your views here.
def registerUser(request):
    if request.method == "POST":
        print(request.POST)
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # assign customer role to user
            user.role = User.CUSTOMER
            form.save()
            return redirect("accounts:registerUser")

    else:
        form = UserForm()

    context = {
        "form": form,
    }
    return render(request, "accounts/registerUser.html", context)
