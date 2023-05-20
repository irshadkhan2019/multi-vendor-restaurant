from django.db import models
from accounts.models import User, UserProfile
from accounts.utils import send_notification
from datetime import time, datetime, date


# Create your models here.
class Vendor(models.Model):
    user = models.OneToOneField(User, related_name="user", on_delete=models.CASCADE)
    user_profile = models.OneToOneField(
        UserProfile, related_name="userprofile", on_delete=models.CASCADE
    )
    vendor_name = models.CharField(max_length=50)
    vendor_slug = models.SlugField(max_length=100, unique=True)

    vendor_license = models.ImageField(upload_to="vendor/license")
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vendor_name

    # check if the vendor/restaurant is open or not
    def is_open(self):
        today_date = date.today()  # eg 2023-02-20
        today = today_date.isoweekday()  # 1,2,3..7
        print("TODAY", today, "today_date", today_date)

        # Check current day's opening hours.
        current_opening_hours = OpeningHour.objects.filter(vendor=self, day=today)

        # time at a particular instance
        now = datetime.now()  # ->eg 2023-02-20 20:11:28.158092
        current_time = now.strftime("%H:%M:%S")  # eg ->20:11:28
        print("now", now, "current_time", current_time)
        print(type(current_time))  # <class 'str'>

        # check if  current time lies b/w opening hrs of todays date
        is_open = None
        for hr in current_opening_hours:
            if not hr.is_closed:
                # start = datetime.strptime(hr.from_hour, "%I:%M %p").time()  #  08:00:00
                # print(type(start))#<class 'datetime.time'>
                start = str(datetime.strptime(hr.from_hour, "%I:%M %p").time())
                end = str(datetime.strptime(hr.to_hour, "%I:%M %p").time())

                print(
                    "start", start, "end", end, type(start)
                )  # start 08:00:00 end 22:30:00 <class 'str'>
                if current_time > start and current_time < end:
                    is_open = True
                    break
                else:
                    is_open = False
        return is_open

    # intercept save fn when model is saved
    def save(self, *args, **kwargs):
        # print("Changes made in Vendor model", (self.user), self.pk)
        if self.pk is not None:
            original = Vendor.objects.get(pk=self.pk)
            # print("OG", original.is_approved)
            # print("NEW", self.is_approved)
            if original.is_approved != self.is_approved:
                mail_template = "accounts/emails/admin_approval_email.html"
                context = {
                    "user": self.user,
                    "is_approved": self.is_approved,
                    "to_email": self.user.email,
                }
                if self.is_approved == True:
                    # Send notification email
                    mail_subject = "Congratulations! Your restaurant has been approved."
                    send_notification(mail_subject, mail_template, context)
                else:
                    # Send notification email
                    mail_subject = "We're sorry! You are not eligible for publishing your food menu on our marketplace."
                    send_notification(mail_subject, mail_template, context)

        return super(Vendor, self).save(*args, **kwargs)


DAYS = [
    (1, ("Monday")),
    (2, ("Tuesday")),
    (3, ("Wednesday")),
    (4, ("Thursday")),
    (5, ("Friday")),
    (6, ("Saturday")),
    (7, ("Sunday")),
]

# list comprehension
HOUR_OF_DAY_24 = [
    (time(hour, minute).strftime("%I:%M %p"), time(hour, minute).strftime("%I:%M %p"))
    for hour in range(0, 24)
    for minute in (0, 30)
]


class OpeningHour(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(choices=HOUR_OF_DAY_24, blank=True, max_length=10)
    to_hour = models.CharField(choices=HOUR_OF_DAY_24, blank=True, max_length=10)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ("day", "-from_hour")
        unique_together = ("vendor", "day", "from_hour", "to_hour")

    # get_fiedname_display() inbuild fn in a Model
    def __str__(self):
        return self.get_day_display()  # to get label Monday instead of value 1
