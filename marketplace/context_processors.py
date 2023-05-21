from .models import Cart, FoodItem, Tax


def get_cart_counter(request):
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart_items = Cart.objects.filter(user=request.user)
            if cart_items:
                for cart_item in cart_items:
                    cart_count += cart_item.quantity
            else:
                cart_count = 0
        except:
            cart_count = 0
    return dict(cart_count=cart_count)


def get_cart_amounts(request):
    subtotal = 0
    tax = 0
    tax_dict = {}
    grand_total = 0

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            fooditem = FoodItem.objects.get(pk=item.fooditem.id)
            subtotal += fooditem.price * item.quantity

        # calculate tax
        get_tax = Tax.objects.filter(is_active=True)
        for tax_item in get_tax:
            tax_type = tax_item.tax_type
            tax_percentage = tax_item.tax_percentage
            tax_amount = round((tax_percentage * subtotal) / 100, 2)
            tax_dict.update({tax_type: {str(tax_percentage): tax_amount}})

        for key, value in tax_dict.items():
            for amt in value.values():
                # print(amt)
                tax += amt
        grand_total = subtotal + tax

    return dict(subtotal=subtotal, tax=tax, grand_total=grand_total, tax_dict=tax_dict)
