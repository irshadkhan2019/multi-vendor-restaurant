from django.core.exceptions import PermissionDenied


def detectUser(user):
    if user.role == 1:
        redirectUrl = "accounts:vendorDashboard"
    elif user.role == 2:
        redirectUrl = "accounts:custDashboard"
    elif user.role == None and user.is_superadmin:
        redirectUrl = "/admin"
    return redirectUrl


def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied
