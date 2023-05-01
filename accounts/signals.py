from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import User, UserProfile


# connect receiver to signal sent by db .
@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    if created:
        # if user is created then create USerProfile for that user
        # print("User Obj was created so will create his profile")
        UserProfile.objects.create(user=instance)
    else:
        # if user updated
        try:
            # print("User Obj was updated so will update his profile")
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except:
            # create userProfile if it does not exist
            # print("User Obj DNE so will create his profile")
            UserProfile.objects.create(user=instance)


@receiver(pre_save, sender=User)
def pre_save_profile_receiver(sender, instance, **kwargs):
    # print("presave-> Will Create user ", instance)
    pass
