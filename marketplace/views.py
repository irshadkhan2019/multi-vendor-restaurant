from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from vendor.models import Vendor
from menu.models import Category, FoodItem
from django.db.models import Prefetch
from .models import Cart


# Create your views here.
def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        "vendors": vendors,
        "vendor_count": vendor_count,
    }
    return render(request, "marketplace/listings.html", context)


def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)

    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        # reverse relationship i.e get all fooditems for a category ,category
        # is fk in FoodItem model.
        Prefetch("fooditems", queryset=FoodItem.objects.filter(is_available=True))
    )

    context = {
        "vendor": vendor,
        "categories": categories,
    }

    return render(request, "marketplace/vendor_detail.html", context)


def add_to_cart(request, food_id):
    print(food_id)
    if request.user.is_authenticated:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            # check if food item exists
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # check if the user has already added that food to cart
                try:
                    checkCart = Cart.objects.get(user=request.user, fooditem=fooditem)

                    # increase cart quantity
                    checkCart.quantity += 1
                    checkCart.save()
                    return JsonResponse(
                        {"status": "Success", "message": "increased the cart quantity"}
                    )
                except:
                    checkCart = Cart.objects.create(
                        user=request.user, fooditem=fooditem, quantity=1
                    )
                    return JsonResponse(
                        {"status": "Success", "message": "Added food to cart"}
                    )
            except:
                return JsonResponse(
                    {"status": "Failed", "message": "Food does not exist"}
                )
        else:
            return JsonResponse({"status": "Failed", "message": "Invalid request"})

    else:
        return JsonResponse(
            {"status": "Failed", "message": "Please login to continue "}
        )
