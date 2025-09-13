import pprint
from django.shortcuts import render, redirect, get_object_or_404
from .models import Event, RecurrenceRule
from .forms import EventForm, RecurrenceRuleForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from datetime import datetime, time, timedelta


def check_form(event_form, request):
    recurrence_form = RecurrenceRuleForm(request.POST)
    is_recurring = request.POST.get('is_recurring') == 'on'
    selected_user_id = request.POST.get('user')
    if event_form.is_valid():
        print("[DEBUG] Event form valid")
    else:
        print("[ERROR] Event form errors:", event_form.errors)
    if is_recurring and not recurrence_form.is_valid():
        print("[ERROR] Recurrence form errors:", recurrence_form.errors)
    return is_recurring, recurrence_form, selected_user_id


def get_or_create_recurrence_rule(type, interval):
    rule = RecurrenceRule.objects.filter(type=type, interval=interval).first()
    if not rule:
        rule = RecurrenceRule.objects.create(type=type, interval=interval)
        print(f"[INFO] Created new recurrence rule: {rule}")
    else:
        print(f"[INFO] Reused existing recurrence rule: {rule}")
    return rule


def apply_end_time_logic(event):
    if not event.end_time:
        dt_start = datetime.combine(datetime.today(), event.start_time)
        dt_end = dt_start + timedelta(hours=1)
        event.end_time = min(dt_end.time(), time(23, 59))
        print(f"[INFO] Auto-set end_time to {event.end_time}")


def create_event(request):
    users = User.objects.all()

    if request.method == 'POST':
        print("\n[DEBUG] --- CREATE POST DATA ---")
        pprint.pprint(dict(request.POST))

        event_form = EventForm(request.POST)
        is_recurring, recurrence_form, selected_user_id = check_form(event_form, request)

        if event_form.is_valid() and (not is_recurring or recurrence_form.is_valid()):
            event = event_form.save(commit=False)
            event.user = User.objects.get(id=selected_user_id)

            if is_recurring:
                recurrence_type = recurrence_form.cleaned_data['type']
                interval = recurrence_form.cleaned_data['interval']
                event.recurrence_rule = get_or_create_recurrence_rule(recurrence_type, interval)

            apply_end_time_logic(event)
            event.save()
            print("[SUCCESS] Created Event:", event)
            return redirect('event_list')

        return render(request, 'create_event.html', {
            'event_form': event_form,
            'recurrence_form': recurrence_form,
            'users': users,
            'selected_user_id': selected_user_id,
        })

    event_form = EventForm()
    recurrence_form = RecurrenceRuleForm()
    return render(request, 'create_event.html', {
        'event_form': event_form,
        'recurrence_form': recurrence_form,
        'users': users
    })


def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    users = User.objects.all()

    if request.method == 'POST':
        print("\n[DEBUG] --- EDIT POST DATA ---")
        pprint.pprint(dict(request.POST))

        event_form = EventForm(request.POST, instance=event)
        is_recurring, recurrence_form, selected_user_id = check_form(event_form, request)

        if event_form.is_valid() and (not is_recurring or recurrence_form.is_valid()):
            event = event_form.save(commit=False)
            event.user = User.objects.get(id=selected_user_id)

            if is_recurring:
                recurrence_type = recurrence_form.cleaned_data['type']
                interval = recurrence_form.cleaned_data['interval']
                event.recurrence_rule = get_or_create_recurrence_rule(recurrence_type, interval)
            else:
                event.recurrence_rule = None

            apply_end_time_logic(event)
            event.save()
            print("[SUCCESS] Updated Event:", event)
            return redirect('event_list')

        return render(request, 'edit_event.html', {
            'event_form': event_form,
            'recurrence_form': recurrence_form,
            'users': users,
            'selected_user_id': selected_user_id,
            'event': event
        })

    event_form = EventForm(instance=event)
    recurrence_form = RecurrenceRuleForm()
    return render(request, 'edit_event.html', {
        'event_form': event_form,
        'recurrence_form': recurrence_form,
        'users': users,
        'event': event,
        'selected_user_id': event.user.id
    })


def event_list(request):
    events = Event.objects.all()
    return render(request, 'event_list.html', {'events': events})


def delete_event(request, event_id):
    event = Event.objects.get(id=event_id)
    event.delete()
    return redirect('event_list')


def filter_events(request):
    events = Event.objects.all()
    users = User.objects.all()

    user_id = request.GET.get("user")
    recurrence = request.GET.get("recurrence")
    name = request.GET.get("name")
    location = request.GET.get("location")
    day = request.GET.get("day")

    if user_id:
        events = events.filter(user__id=user_id)

    if recurrence:
        if recurrence == "none":
            events = events.filter(recurrence_rule__isnull=True)
        else:
            events = events.filter(recurrence_rule__type=recurrence)

    if name:
        events = events.filter(name__icontains=name)

    if location:
        events = events.filter(location__icontains=location)

    if day:
        events = events.filter(day=day)

    return render(request, 'filter_events.html', {
        'events': events,
        'users': users
    })


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('event_list')
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})
