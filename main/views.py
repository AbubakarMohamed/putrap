import googlemaps
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Route, Preferences
from .forms import RouteForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from .forms import FeedbackForm
from django.shortcuts import render, redirect
from django.contrib.auth import logout
import heapq
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import Route, Preferences
from .utils import dijkstra

# Example graph structure
graph = {
    'A': {'B': 1, 'C': 4},
    'B': {'A': 1, 'C': 2, 'D': 5},
    'C': {'A': 4, 'B': 2, 'D': 1},
    'D': {'B': 5, 'C': 1},
}

@method_decorator(csrf_exempt, name='dispatch')
class RoutePlanningView(View):
    def post(self, request):
        origin = request.POST.get('origin')
        destination = request.POST.get('destination')
        
        if origin not in graph or destination not in graph:
            return JsonResponse({'error': 'Invalid origin or destination'}, status=400)
        
        path, cost = dijkstra(graph, origin, destination)
        
        return JsonResponse({'path': path, 'cost': cost})

# Utility function to perform Dijkstra's algorithm
def dijkstra(graph, start, goal):
    queue = [(0, start, [])]
    seen = set()
    min_heap = {start: 0}
    
    while queue:
        (cost, node, path) = heapq.heappop(queue)
        
        if node in seen:
            continue
        
        path = path + [node]
        seen.add(node)
        
        if node == goal:
            return (path, cost)
        
        for neighbor, weight in graph[node].items():
            if neighbor in seen:
                continue
            
            prev = min_heap.get(neighbor, None)
            next_cost = cost + weight
            if prev is None or next_cost < prev:
                min_heap[neighbor] = next_cost
                heapq.heappush(queue, (next_cost, neighbor, path))
    
    return ([], float("inf"))


@login_required
def feedback(request, route_id):
      route = Route.objects.get(id=route_id)
      if request.method == "POST":
          form = FeedbackForm(request.POST)
          if form.is_valid():
              feedback = form.save(commit=False)
              feedback.user = request.user
              feedback.route = route
              feedback.save()
              return redirect('home')
      else:
          form = FeedbackForm()
      return render(request, 'feedback.html', {'form': form, 'route': route})
 
@login_required
def profile(request):
      if request.method == "POST":
          form = ProfileForm(request.POST, instance=request.user)
          if form.is_valid():
              form.save()
              return redirect('profile')
      else:
          form = ProfileForm(instance=request.user)
      return render(request, 'profile.html', {'form': form})
  
def register(request):
      if request.method == "POST":
          form = UserCreationForm(request.POST)
          if form.is_valid():
              user = form.save()
              login(request, user)
              return redirect('home')
      else:
          form = UserCreationForm()
      return render(request, 'register.html', {'form': form})

def login_view(request):
      if request.method == "POST":
          form = AuthenticationForm(request, data=request.POST)
          if form.is_valid():
              user = form.get_user()
              login(request, user)
              return redirect('home')
      else:
          form = AuthenticationForm()
      return render(request, 'login.html', {'form': form})

@login_required
def route_suggestions(request):
    if request.method == "POST":
        form = RouteForm(request.POST)
        if form.is_valid():
            origin = form.cleaned_data['origin']
            destination = form.cleaned_data['destination']
            user = request.user

            # Initialize Google Maps client
            gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

            # Request directions via driving and transit modes
            routes = []
            for mode in ['driving', 'transit']:
                directions_result = gmaps.directions(origin, destination, mode=mode)
                if directions_result:
                    route_info = directions_result[0]
                    route = Route.objects.create(
                        user=user,
                        origin=origin,
                        destination=destination,
                        route_details=route_info['summary'],
                        estimated_time=route_info['legs'][0]['duration']['value'] // 60,  # Convert seconds to minutes
                        estimated_cost=calculate_cost(route_info, mode),  # You need to define this function
                        route_number=mode
                    )
                    routes.append(route)
            
            return render(request, 'suggestions.html', {'routes': routes})
    else:
        form = RouteForm()
    return render(request, 'route_form.html', {'form': form})

def calculate_cost(route_info, mode):
    # Define a function to calculate cost based on the mode of transport
    if mode == 'driving':
        return route_info['legs'][0]['distance']['value'] / 1000 * 0.5  # Example: $0.5 per km
    elif mode == 'transit':
        return 2.5  # Example: flat rate for transit
    return 0

@login_required
def real_time_updates(request):
      # Fetch real-time updates from an API (e.g., traffic updates)
      updates = real_time_updates()  # Implement this function
      return render(request, 'real_time_updates.html', {'updates': updates})

def logout_view(request):
    logout(request)
    return redirect('login')

from django.shortcuts import render

def home(request):
    return render(request, 'home.html')