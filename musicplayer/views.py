from django.http import HttpResponse
from django.shortcuts import render
from .models import SongsData
from gtts import gTTS
import os
from playsound import playsound
import speech_recognition as sr
import json
from django.http import JsonResponse

file = "good"
i="0"

def texttospeech(text, filename):
    filename = filename + '.mp3'
    flag = True
    while flag:
        try:
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(filename)
            flag = False
        except:
            print('Trying again')
    playsound(filename)
    os.remove(filename)
    return

def speechtotext(duration):
    global i
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        playsound('speak.mp3')
        audio = r.listen(source, phrase_time_limit=duration)
    try:
        response = r.recognize_google(audio)
    except:
        response = 'N'
    return response

def homepage(request):
    if request.method == 'GET':
        songs = SongsData.objects.all()
        return render(request, 'musicplayer/frontmusic.html', {'songs':songs})
    else:
        key = request.POST.get('key_code')
        print("char pressed = " + key)
        return JsonResponse({'result' : key})
