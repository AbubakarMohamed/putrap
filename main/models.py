# main/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  
        blank=True,
        help_text=('The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
        related_query_name='customuser'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',  
        blank=True,
        help_text=('Specific permissions for this user.'),
        related_query_name='customuser'
    )



class Preferences(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    transportation_mode = models.CharField(max_length=50)
    max_travel_time = models.IntegerField()
    max_cost = models.DecimalField(max_digits=10, decimal_places=2)
    environmental_impact_preference = models.CharField(max_length=50)

class Route(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    route_details = models.TextField()
    estimated_time = models.IntegerField()
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2)
    route_number = models.IntegerField()  # to distinguish between multiple routes for the same request

class Feedback(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    comments = models.TextField()
    rating = models.IntegerField()
