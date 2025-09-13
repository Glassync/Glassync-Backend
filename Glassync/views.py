from django.shortcuts import render, redirect
from .models import Event
from .forms import EventForm
from django.contrib.auth.models import User


# Create Event
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('event_list')  # Redirect to event list after creation
    else:
        form = EventForm()
    return render(request, 'create_event.html', {'form': form})


# List Events
def event_list(request):
    events = Event.objects.all()
    return render(request, 'event_list.html', {'events': events})


# Delete Event
def delete_event(request, event_id):
    event = Event.objects.get(id=event_id)
    event.delete()
    return redirect('event_list')  # Redirect to event list after deletion


# Edit Event
def edit_event(request, event_id):
    event = Event.objects.get(id=event_id)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_list')
    else:
        form = EventForm(instance=event)
    return render(request, 'edit_event.html', {'form': form})


def filter_events(request):
    selected_user = None
    if 'user' in request.GET:
        selected_user = User.objects.get(id=request.GET['user'])
        events = Event.objects.filter(user=selected_user)
    else:
        events = Event.objects.all()

    users = User.objects.all()  # To display in the dropdown
    return render(request, 'filter_events.html',
                  {'events': events, 'users': users, 'selected_user': selected_user})


def event_list(request):
    events = Event.objects.all()
    return render(request, 'event_list.html', {'events': events})