from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),                                                                                        # ← Новый маршрут
    path('', views.home, name='home'),                                                                                      # ← Новый маршрут
    path('create/', views.create_calendar, name='create_calendar'),
    path('calendar/<uuid:calendar_id>/', views.calendar_view, name='calendar_view'),
    path('calendar/<uuid:calendar_id>/<int:year>/<int:month>/', views.calendar_view, name='calendar_view_with_params'),
    path('calendar/<str:calendar_name>/enter/', views.enter_calendar, name='enter_calendar'),                               # ← Новый маршрут
    path('calendar/<uuid:calendar_id>/get_events/', views.get_events, name='get_events'),
    path('calendar/<uuid:calendar_id>/add_event/', views.add_event, name='add_event'),
    path('calendar/<uuid:calendar_id>/edit_event/<int:event_id>/', views.edit_event, name='edit_event'),
    path('calendar/<uuid:calendar_id>/delete_event/<int:event_id>/', views.delete_event, name='delete_event'),
]

