# ./calendar_project/urls.py

from django.urls import path, include

urlpatterns = [
    path('', include('calendar_app.urls')),
]