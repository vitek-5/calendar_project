from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.utils import timezone
import calendar as calendar_lib
from datetime import datetime
from .models import Calendar, Event
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

ru_months = {
    1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель',
    5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
    9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'
}
ru_week_days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']


def home(request):
    calendars = Calendar.objects.all().order_by('-created_at')
    return render(request, 'home.html', {'calendars': calendars})


@csrf_exempt
def create_calendar(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if not name or len(name.strip()) == 0:
            messages.error(request, "Название календаря обязательно!")
            return render(request, 'create_calendar.html', {'error': True})
        calendar = Calendar.objects.create(name=name.strip())
        return redirect('calendar_view', calendar_id=calendar.id)
    return render(request, 'create_calendar.html')


@csrf_protect
def enter_calendar(request, calendar_name):
    try:
        calendar = Calendar.objects.get(name=calendar_name)
    except Calendar.DoesNotExist:
        messages.error(request, "Календарь не найден.")
        return redirect('home')

    if request.method == 'POST':
        entered_uuid = request.POST.get('uuid')
        if str(calendar.id) == entered_uuid:
            return redirect('calendar_view', calendar_id=calendar.id)
        else:
            messages.error(request, "Неверный пароль (UUID).")

    return render(request, 'enter_calendar.html', {'calendar_name': calendar.name})


def calendar_view(request, calendar_id, year=None, month=None):
    calendar = get_object_or_404(Calendar, id=calendar_id)
    now = timezone.now()
    if not year:
        year = now.year
    if not month:
        month = now.month
    try:
        month_dates = calendar_lib.Calendar().monthdatescalendar(year, month)
    except ValueError:
        year = now.year
        month = now.month
        month_dates = calendar_lib.Calendar().monthdatescalendar(year, month)

    weeks = []
    for week in month_dates:
        new_week = []
        for date in week:
            is_current_month = (date.month == month)
            new_week.append((date.day, date.strftime('%Y-%m-%d'), not is_current_month))
        weeks.append(new_week)

    events = Event.objects.filter(calendar=calendar, date__year=year, date__month=month)
    events_by_day = {}
    for event in events:
        key = event.date.strftime('%Y-%m-%d')
        events_by_day.setdefault(key, []).append(event)

    years_per_page = 15
    current_page = int(request.GET.get('page', (year - 1900) // years_per_page))
    start_year = 1900 + current_page * years_per_page
    end_year = start_year + years_per_page - 1
    years_grid = list(range(start_year, end_year + 1))
    prev_page = current_page - 1 if start_year > 1900 else None
    next_page = current_page + 1 if end_year < 2100 else None

    context = {
        'calendar': calendar,
        'year': year,
        'month': month,
        'month_name': ru_months[month],
        'ru_months': ru_months,
        'ru_week_days': ru_week_days,
        'weeks': weeks,
        'events_by_day': events_by_day,
        'prev_year': year - 1 if month == 1 else year,
        'prev_month': 12 if month == 1 else month - 1,
        'next_year': year + 1 if month == 12 else year,
        'next_month': 1 if month == 12 else month + 1,
        'years_grid': years_grid,
        'current_page': current_page,
        'prev_page': prev_page,
        'next_page': next_page,
        'start_year': start_year,
        'end_year': end_year,
        'current_year': now.year,
        'base_calendar_url': request.build_absolute_uri(f'/calendar/{calendar.id}/'),
    }
    return render(request, 'calendar.html', context)


@csrf_exempt
def add_event(request, calendar_id):
    if request.method == 'POST':
        calendar = get_object_or_404(Calendar, id=calendar_id)
        title = request.POST.get('title')
        description = request.POST.get('description')
        date_str = request.POST.get('date')
        try:
            year, month, day = map(int, date_str.split('-'))
            date = datetime(year, month, day).date()
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid date'})
        Event.objects.create(
            calendar=calendar,
            title=title,
            description=description,
            date=date
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@csrf_exempt
def edit_event(request, calendar_id, event_id):
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id, calendar_id=calendar_id)
        event.title = request.POST.get('title', event.title)
        event.description = request.POST.get('description', event.description)
        event.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})


@csrf_exempt
def delete_event(request, calendar_id, event_id):
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id, calendar_id=calendar_id)
        event.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})


@csrf_exempt
def get_events(request, calendar_id):
    date_str = request.GET.get('date')
    try:
        year, month, day = map(int, date_str.split('-'))
        date = datetime(year, month, day).date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date'}, status=400)

    calendar = get_object_or_404(Calendar, id=calendar_id)
    events = Event.objects.filter(calendar=calendar, date=date)
    events_data = [{'id': e.id, 'title': e.title, 'description': e.description} for e in events]
    return JsonResponse({'events': events_data})


@login_required
def delete_calendar(request, calendar_id):
    calendar = get_object_or_404(Calendar, id=calendar_id)
    calendar.delete()
    messages.success(request, "Календарь успешно удален.")
    return redirect('home')