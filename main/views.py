from django.shortcuts import render
from vendor.models import Vendor
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance


# Create your views here.
def home(request):
    if "lat" and "lng" in request.GET:
        lat = request.GET.get("lat")
        lng = request.GET.get("lng")
        pnt = GEOSGeometry("POINT(%s %s)" % (lng, lat))
        vendors = (
            Vendor.objects.filter(
                user_profile__location__distance_lte=(pnt, D(km=100))
            )  # adds calculated distance field to each vendor wrt to pnt
            .annotate(distance=Distance("user_profile__location", pnt))
            .order_by("distance")
        )
        # add distance as km field
        for vendor in vendors:
            vendor.kms = round(vendor.distance.km, 1)

    else:
        vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:5]

    context = {
        "vendors": vendors,
    }
    return render(request, "home.html", context)
