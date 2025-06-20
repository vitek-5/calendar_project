# ./calendar_app/admin.py

# Register your models here.
from django.contrib import admin
from .models import Calendar, Event

@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'created_at')
    search_fields = ('name',)
    ordering = ('-created_at',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'calendar', 'date')
    list_filter = ('calendar',)
    search_fields = ('title',)