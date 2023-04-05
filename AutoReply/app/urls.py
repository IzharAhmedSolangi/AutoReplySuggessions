from django.urls import path
from .views import AutoReplyView

urlpatterns = [
    path('autoreply/', AutoReplyView.as_view(), name='autoreply'),
]