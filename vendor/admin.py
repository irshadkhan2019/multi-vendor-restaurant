from django.contrib import admin
from vendor.models import Vendor


# Register your models here.
class vendorAdmin(admin.ModelAdmin):
    pass


admin.site.register(Vendor, vendorAdmin)
