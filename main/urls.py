from django.urls import path
from . import views
from django.urls import path
from .views import RoutePlanningView

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('home/', views.home, name='home'),
    path('plan_route/', RoutePlanningView.as_view(), name='plan_route'),
    path('suggestions/', views.route_suggestions, name='route_suggestions'),
    path('feedback/<int:route_id>/', views.feedback, name='feedback'),
    path('real_time_updates/', views.real_time_updates, name='real_time_updates'),
]
