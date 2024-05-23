from django.urls import path
from .views import process_music, check_status


urlpatterns = [
    path('process-music/', upload_music, name='upload_music'),
    path('check_status/', check_status, name='check_status')
]