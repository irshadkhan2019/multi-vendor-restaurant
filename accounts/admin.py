from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your models here.
class CustomUserAdmin(UserAdmin):
    list_display=('email', 'first_name', 'last_name', 'username', 'role', 'is_active')
    filter_horizontal = ()
    list_filter = ()

admin.site.register(User,CustomUserAdmin)

    