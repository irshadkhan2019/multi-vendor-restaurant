from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from vendor.models import Vendor
from menu.models import Category, FoodItem
from django.db.models import Prefetch
from .models import Cart
from .context_processors import get_cart_counter, get_cart_amounts
from django.contrib.auth.decorators import login_required


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
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None

    context = {
        "vendor": vendor,
        "categories": categories,
        "cart_items": cart_items,
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
                    # A Cart having a fooditem
                    checkCart = Cart.objects.get(user=request.user, fooditem=fooditem)

                    # increase cart quantity
                    checkCart.quantity += 1
                    checkCart.save()
                    return JsonResponse(
                        {
                            "status": "Success",
                            "message": "increased the cart quantity",
                            "cart_counter": get_cart_counter(request),
                            "quantity": checkCart.quantity,
                            "cart_amount": get_cart_amounts(request),
                        }
                    )
                except:
                    checkCart = Cart.objects.create(
                        user=request.user, fooditem=fooditem, quantity=1
                    )
                    return JsonResponse(
                        {
                            "status": "Success",
                            "message": "Added food to cart",
                            "cart_counter": get_cart_counter(request),
                            "quantity": checkCart.quantity,
                            "cart_amount": get_cart_amounts(request),
                        }
                    )
            except:
                return JsonResponse(
                    {"status": "Failed", "message": "Food does not exist"}
                )
        else:
            return JsonResponse({"status": "Failed", "message": "Invalid request"})

    else:
        return JsonResponse(
            {"status": "login_required", "message": "Please login to continue "}
        )


def decrease_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            # Check if the food item exists
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # Check if the user has already added that food to the cart
                try:
                    checkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    if checkCart.quantity > 1:
                        # decrease the cart quantity
                        checkCart.quantity -= 1
                        checkCart.save()
                    else:
                        checkCart.delete()
                        checkCart.quantity = 0
                    return JsonResponse(
                        {
                            "status": "Success",
                            "message": "Removed fooditem from cart",
                            "cart_counter": get_cart_counter(request),
                            "quantity": checkCart.quantity,
                            "cart_amount": get_cart_amounts(request),
                        }
                    )
                except:
                    return JsonResponse(
                        {
                            "status": "Failed",
                            "message": "You do not have this item in your cart!",
                        }
                    )
            except:
                return JsonResponse(
                    {"status": "Failed", "message": "This food does not exist!"}
                )
        else:
            return JsonResponse({"status": "Failed", "message": "Invalid request!"})

    else:
        return JsonResponse(
            {"status": "login_required", "message": "Please login to continue"}
        )


@login_required(login_url="login")
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    print(cart_items)
    context = {
        "cart_items": cart_items,
    }
    return render(request, "marketplace/cart.html", context)


def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            try:
                # Get cart item with specific id for user
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse(
                        {
                            "status": "Success",
                            "message": "Cart item has been deleted!",
                            "cart_counter": get_cart_counter(request),
                            "cart_amount": get_cart_amounts(request),
                        }
                    )
            except:
                return JsonResponse(
                    {"status": "Failed", "message": "Cart Item does not exist!"}
                )
        else:
            return JsonResponse({"status": "Failed", "message": "Invalid request!"})


def search(request):
    address = request.GET["address"]
    latitude = request.GET["lat"]
    longitude = request.GET["lng"]
    keyword = request.GET["keyword"]
    radius = request.GET["radius"]

    vendors = Vendor.objects.filter(
        vendor_name__icontains=keyword,
        is_approved=True,
        user__is_active=True,
    )
    vendor_count = vendors.count()

    context = {
        "vendors": vendors,
        "vendor_count": vendor_count,
    }
    return render(request, "marketplace/listings.html", context)
