from django.http import HttpResponse
from django.shortcuts import render
from .models import SongsData

def homepage(request):
    songs = SongsData.objects.all()
    return render(request, 'musicplayer/Music Player.html', {'songs':songs})