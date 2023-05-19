from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from .forms import VendorForm, OpeningHourForm
from accounts.forms import UserProfileForm
from django.db import IntegrityError

from accounts.models import UserProfile
from .models import Vendor, OpeningHour
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.utils import check_role_vendor
from menu.models import Category, FoodItem
from menu.forms import CategoryForm, FoodItemForm
from django.template.defaultfilters import slugify


# Create your views here.
@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def vprofile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == "POST":
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)

        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, "Settings updated.")
            return redirect("accounts:vendor:vprofile")
        else:
            print(profile_form.errors)
            print(vendor_form.errors)
    else:
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)

    context = {
        "profile_form": profile_form,
        "vendor_form": vendor_form,
        "profile": profile,
        "vendor": vendor,
    }
    return render(request, "vendor/vprofile.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def menu_builder(request):
    vendor = Vendor.objects.get(user=request.user)
    categories = Category.objects.filter(vendor=vendor)
    print(categories)
    context = {
        "categories": categories,
    }
    return render(request, "vendor/menu_builder.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def fooditems_by_category(request, pk):
    vendor = Vendor.objects.get(user=request.user)
    category = get_object_or_404(Category, pk=pk)
    fooditems = FoodItem.objects.filter(vendor=vendor, category=category)
    context = {
        "fooditems": fooditems,
        "category": category,
    }
    return render(request, "vendor/fooditems_by_category.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data["category_name"]
            category = form.save(commit=False)
            category.vendor = Vendor.objects.get(user=request.user)
            category.save()
            category.slug = slugify(category_name) + "-" + str(category.pk)
            category.save()
            messages.success(request, "Category added successfully!")
            return redirect("accounts:vendor:menu_builder")
        else:
            print(form.errors)

    else:
        form = CategoryForm()
    context = {
        "form": form,
    }
    return render(request, "vendor/add_category.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category_name = form.cleaned_data["category_name"]
            category = form.save(commit=False)
            category.vendor = Vendor.objects.get(user=request.user)
            category.slug = slugify(category_name)
            form.save()
            messages.success(request, "Category updated successfully!")
            return redirect("accounts:vendor:menu_builder")
        else:
            print(form.errors)

    else:
        form = CategoryForm(instance=category)
    context = {
        "form": form,
        "category": category,
    }
    return render(request, "vendor/edit_category.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def delete_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, "Category has been deleted successfully!")
    return redirect("accounts:vendor:menu_builder")


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def add_food(request):
    if request.method == "POST":
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            foodtitle = form.cleaned_data["food_title"]
            food = form.save(commit=False)
            food.vendor = Vendor.objects.get(user=request.user)
            food.slug = slugify(foodtitle) + "-" + str(food.pk)
            form.save()
            messages.success(request, "Food Item added successfully!")
            # Rediect to display all foods that belongs to this food category
            return redirect("accounts:vendor:fooditems_by_category", food.category.id)
        else:
            print(form.errors)
    else:
        form = FoodItemForm()
        # get categories that belong to the current vendor
        form.fields["category"].queryset = Category.objects.filter(
            vendor=Vendor.objects.get(user=request.user)
        )

    context = {
        "form": form,
    }
    return render(request, "vendor/add_food.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def edit_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    if request.method == "POST":
        form = FoodItemForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            foodtitle = form.cleaned_data["food_title"]
            food = form.save(commit=False)
            food.vendor = Vendor.objects.get(user=request.user)
            food.slug = slugify(foodtitle)
            form.save()
            messages.success(request, "Food Item updated successfully!")
            return redirect("accounts:vendor:fooditems_by_category", food.category.id)
        else:
            print(form.errors)

    else:
        form = FoodItemForm(instance=food)
        form.fields["category"].queryset = Category.objects.filter(
            vendor=Vendor.objects.get(user=request.user)
        )

    context = {
        "form": form,
        "food": food,
    }
    return render(request, "vendor/edit_food.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def delete_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    food.delete()
    messages.success(request, "Food Item has been deleted successfully!")
    return redirect("accounts:vendor:fooditems_by_category", food.category.id)


def opening_hours(request):
    # get all opening hrs for a vendor
    opening_hours = OpeningHour.objects.filter(
        vendor=Vendor.objects.get(user=request.user)
    )

    # create form
    form = OpeningHourForm()
    context = {
        "form": form,
        "opening_hours": opening_hours,
    }

    return render(request, "vendor/opening_hours.html", context)


def add_opening_hours(request):
    if request.user.is_authenticated:
        if (  # check if its ajax resource
            request.headers.get("x-requested-with") == "XMLHttpRequest"
            and request.method == "POST"
        ):
            day = request.POST.get("day")
            from_hour = request.POST.get("from_hour")
            to_hour = request.POST.get("to_hour")
            is_closed = request.POST.get("is_closed")
            print(day, from_hour, to_hour, is_closed)

            try:
                hour = OpeningHour.objects.create(
                    vendor=Vendor.objects.get(user=request.user),
                    day=day,
                    from_hour=from_hour,
                    to_hour=to_hour,
                    is_closed=is_closed,
                )

                if hour:
                    day = OpeningHour.objects.get(pk=hour.pk)

                    if day.is_closed:
                        response = {
                            "status": "success",
                            "id": hour.pk,
                            "day": day.get_day_display(),
                            "is_closed": "Closed",
                        }
                    else:
                        response = {
                            "status": "success",
                            "id": hour.pk,
                            "day": day.get_day_display(),
                            "from_hour": hour.from_hour,
                            "to_hour": hour.to_hour,
                        }
                return JsonResponse(response)
            except IntegrityError as e:
                response = {
                    "status": "failed",
                    "message": from_hour
                    + "-"
                    + to_hour
                    + " already exists for this day!",
                }
                return JsonResponse(response)
        else:
            return HttpResponse("Invalid Request")
