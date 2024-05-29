from django import forms
from .models import Route
from django import forms
from django.contrib.auth.models import User
from django import forms
from .models import Feedback
  
class FeedbackForm(forms.ModelForm):
      class Meta:
          model = Feedback
          fields = ['comments', 'rating']
 
class ProfileForm(forms.ModelForm):
      class Meta:
          model = User
          fields = ['first_name', 'last_name', 'email']

class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['origin', 'destination']
