from django.http import HttpResponse
from django.shortcuts import render, redirect
from marketplace.models import Cart
from marketplace.context_processors import get_cart_amounts
from .forms import OrderForm
from .models import Order, OrderedFood, Payment
import simplejson as json
from .utils import generateOrderNumber


# Create your views here.
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by("created_at")
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect("market:marketplace")
    cart_details = get_cart_amounts(request)
    # print(cart_details)
    # print("::::", request.POST)
    subtotal = cart_details["subtotal"]
    total_tax = cart_details["tax"]
    grand_total = cart_details["grand_total"]
    tax_data = cart_details["tax_dict"]
    # print(subtotal, tax_data, grand_total, total_tax)

    if request.method == "POST":
        # pass post data to orderForm
        form = OrderForm(request.POST)
        if form.is_valid():
            # print(form.cleaned_data)
            # create Order instance and fill values
            order = Order()
            order.first_name = form.cleaned_data["first_name"]
            order.last_name = form.cleaned_data["last_name"]
            order.phone = form.cleaned_data["phone"]
            order.email = form.cleaned_data["email"]
            order.address = form.cleaned_data["address"]
            order.country = form.cleaned_data["country"]
            order.state = form.cleaned_data["state"]
            order.city = form.cleaned_data["city"]
            order.pin_code = form.cleaned_data["pin_code"]
            order.user = request.user
            order.total = grand_total
            order.tax_data = json.dumps(tax_data)
            order.total_tax = total_tax
            order.payment_method = request.POST["payment_method"]
            order.save()  # order id/ pk is generated
            order.order_number = generateOrderNumber(order.pk)
            order.save()
            # print(order)
            context = {"order": order, "cart_items": cart_items}

            return render(request, "orders/place_order.html", context)
    return render(request, "orders/place_order.html")


def payments(request):
    # Check if the request is ajax or not
    if (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        and request.method == "POST"
    ):
        # STORE THE PAYMENT DETAILS IN THE PAYMENT MODEL
        order_number = request.POST.get("order_number")
        transaction_id = request.POST.get("transaction_id")
        payment_method = request.POST.get("payment_method")
        status = request.POST.get("status")

        order = Order.objects.get(user=request.user, order_number=order_number)
        payment = Payment(
            user=request.user,
            transaction_id=transaction_id,
            payment_method=payment_method,
            amount=order.total,
            status=status,
        )
        payment.save()

        # UPDATE THE ORDER MODEL
        order.payment = payment
        order.is_ordered = True
        order.save()

        # move cart item to ordered food model
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            ordered_food = OrderedFood()
            ordered_food.order = order
            ordered_food.payment = payment
            ordered_food.user = request.user
            ordered_food.fooditem = item.fooditem
            ordered_food.quantity = item.quantity
            ordered_food.price = item.fooditem.price
            ordered_food.amount = item.fooditem.price * item.quantity
            ordered_food.save()

    return HttpResponse(payment, order)
