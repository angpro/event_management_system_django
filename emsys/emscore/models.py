from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class EventDetails(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='event_author')
    create_data = models.DateTimeField(auto_now = True)
    title = models.CharField(max_length=300)
    address = models.CharField(max_length=300)
    time = models.DateTimeField()
    description = models.TextField()

    booked_by = models.ManyToManyField(User, related_name='users_booked_event')
    attendants = models.ManyToManyField(User, related_name='useds_attendant_event')

    def __str__(self):
        return self.title


class SubscriptionDb(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    subscribed_by = models.ManyToManyField(User, related_name='users_subscribed')
