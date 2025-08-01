 # Replace any imp usage with:
from django.shortcuts import render
from django.http import HttpResponse
import importlib
from importlib import util
import importlib.metadata
from django.shortcuts import render, redirect
from notification.models import Notification

def ShowNotification(request):
    user = request.user
    notifications = Notification.objects.filter(user=user).order_by('-date')

    context = {
        'notifications': notifications,

    }
    return render(request, 'notifications/notification.html', context)

def DeleteNotification(request, noti_id):
    user = request.user
    Notification.objects.filter(id=noti_id, user=user).delete()
    return redirect('show-notification')
