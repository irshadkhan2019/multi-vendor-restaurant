import os
from django.core.exceptions import ValidationError


def allow_only_images_validator(value):
    extension = os.path.splitext(value.name)[1]
    print(extension)
    valid_extensions = [".png", ".jpg", ".jpeg", ".pdf"]
    if not extension.lower() in valid_extensions:
        raise ValidationError(
            "Unsupported file extension. Allowed extensions: " + str(valid_extensions)
        )
