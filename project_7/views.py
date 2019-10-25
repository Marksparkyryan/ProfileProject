from django.shortcuts import render

from accounts.models import User


def home(request):
    carousel_users = User.objects.all()[:10]
    return render(request, 'home.html', {'users': carousel_users})