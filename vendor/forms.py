from django import forms
from .models import Vendor


class VendorForm(forms.ModelForm):
    vendor_license = forms.FileField(
        widget=forms.FileInput(attrs={"class": "btn btn-info"})
    )

    class Meta:
        model: Vendor = Vendor
        fields = ["vendor_name", "vendor_license"]
