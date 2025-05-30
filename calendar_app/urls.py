# ./calendar_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_calendar, name='create_calendar'),
    path('calendar/<uuid:calendar_id>/', views.calendar_view, name='calendar_view'),
    path('calendar/<uuid:calendar_id>/<int:year>/<int:month>/', views.calendar_view, name='calendar_view_with_params'),
    path('calendar/<uuid:calendar_id>/get_events/', views.get_events, name='get_events'),
    path('calendar/<uuid:calendar_id>/add_event/', views.add_event, name='add_event'),
    path('calendar/<uuid:calendar_id>/edit_event/<int:event_id>/', views.edit_event, name='edit_event'),
    path('calendar/<uuid:calendar_id>/delete_event/<int:event_id>/', views.delete_event, name='delete_event'),
]