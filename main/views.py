from django.shortcuts import render
from vendor.models import Vendor


# Create your views here.
def home(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:5]
    print(vendors)
    context = {
        "vendors": vendors,
    }
    return render(request, "home.html", context)
