from django.http import HttpResponse
from django.shortcuts import render
from .models import SongsData
from gtts import gTTS
import os
from playsound import playsound
import speech_recognition as sr
from django.http import JsonResponse
from random import randint
import cv2
import numpy as np
import math

file = "good"
i = "0"
time = 0


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


def getSongsList():
    songs = SongsData.objects.all()
    songs = list(songs)
    list_of_songs = []
    for song in songs:
        song_dict = dict()
        song_dict['Name'] = song.Name
        song_dict['Singer'] = song.Singer
        lyrics = song.Lyrics.split("\r\n")
        song_dict['Lyrics'] = lyrics
        song_dict['Audio'] = song.Audio
        song_dict['Thumbnail'] = song.Thumbnail
        song_dict['Category'] = song.Category
        list_of_songs.append(song_dict)
    return list_of_songs


def getGestureAction():
    count = 0
    cap = cv2.VideoCapture(0)
    count1 = 0
    count2 = 0
    count3 = 0
    action = str()
    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        kernel = np.ones((3, 3), np.uint8)

        # define region of interest
        roi = frame[200:400, 400:600]
        cv2.rectangle(frame, (400, 200), (600, 400), (0, 255, 0), 0)
        cv2.imwrite("check%d.jpg" % count, roi)
        image = cv2.imread("check%d.jpg" % count)
        os.remove("check%d.jpg" % count)
        count = count + 1
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower_skin, upper_skin)

        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if contours == []:
            cv2.putText(frame, "Nothing in frame ", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            continue

        cnt = max(contours, key=lambda x: cv2.contourArea(x))
        epsilon = 0.0005 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        hull = cv2.convexHull(approx, returnPoints=False)
        defects = cv2.convexityDefects(approx, hull)
        if defects is None:
            cv2.putText(frame, "Nothing in frame ", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            continue
        # l = no. of defects
        l = 0
        for i in range(defects.shape[0]):
            s, e, f, d = defects[i, 0]
            start = tuple(approx[s][0])
            end = tuple(approx[e][0])
            far = tuple(approx[f][0])
            pt = (100, 180)

            # find length of all sides of triangle
            a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
            b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
            c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
            s = (a + b + c) / 2
            ar = math.sqrt(s * (s - a) * (s - b) * (s - c))

            # distance between point and convex hull
            d = (2 * ar) / a

            # apply cosine rule here
            angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 57

            # ignore angles > 90 and ignore points very close to convex hull(they generally come due to noise)
            if angle <= 90 and d > 20:
                l += 1

        if l == 0:
            cv2.putText(frame, "Nothing in frame ", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            count1 = 0
            count2 = 0
            count3 = 0
        elif l == 1:
            count1 = count1 + 1
        elif l == 2:
            count2 = count2 + 1
        else:
            count3 = count3 + 1

        if count1 > 20:
            cv2.putText(frame, "symbol 1", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            action = "play_pause"
            break
        elif count2 > 20:
            cv2.putText(frame, "symbol 2", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            action = "next"
            break
        elif count3 > 20:
            cv2.putText(frame, "symbol 3", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            action = "previous"
            break

        cv2.imshow('Input', frame)
        c = cv2.waitKey(1)
        if c == 27:
            break
    cap.release()
    cv2.destroyAllWindows()
    return action


def generateResponse(action):
    resp = dict()

    if action == 'play':
        resp['play'] = 'true'
    else:
        resp['play'] = 'false'

    if action == 'pause':
        resp['pause'] = 'true'
    else:
        resp['pause'] = 'false'

    if action == 'next':
        resp['next'] = 'true'
    else:
        resp['next'] = 'false'

    if action == 'current':
        resp['current'] = 'true'
    else:
        resp['current'] = 'false'

    if action == 'previous':
        resp['previous'] = 'true'
    else:
        resp['previous'] = 'false'

    if action == 'play_pause':
        resp['play_pause'] = 'true'
    else:
        resp['play_pause'] = 'false'

    if action == 'volume':
        resp['volume'] = 'true'
    else:
        resp['volume'] = 'false'

    return resp


def homepage(request):
    global i, time
    if request.method == 'GET':
        songs = getSongsList()
        return render(request, 'musicplayer/frontmusic.html', {'songs': songs})

    else:
        key = request.POST.get('key_code')
        print("char pressed = " + key)
        if key == 'Esc':
            if time == 0:
                texttospeech("Speak PLAY to play a random song, PAUSE, to pause the current playing song, NEXT, "
                             "to play the next song, PREVIOUS, to play the previous song, CURRENT, to play the "
                             "currently paused song, volume along with percentage to adjust the volume.", file + i)
                i = i + str(1)
                time = 1
            say = speechtotext(4)
            print(say)
            if say == 'play':
                songs = getSongsList()
                num_of_songs = len(songs)
                num = randint(0, num_of_songs)
                print(num_of_songs)
                print(songs[num]['Name'])
                resp = generateResponse('play')
                resp['song_name'] = songs[num]['Name']
                return JsonResponse({'result': resp})
            elif say == 'pause':
                resp = generateResponse('pause')
                return JsonResponse({'result': resp})
            elif say == 'next':
                resp = generateResponse('next')
                return JsonResponse({'result': resp})
            elif say == 'previous':
                resp = generateResponse('previous')
                return JsonResponse({'result': resp})
            elif say == 'current':
                resp = generateResponse('current')
                return JsonResponse({'result': resp})
            elif say[0 : say.find(' ')] == 'volume':
                resp = generateResponse('volume')
                resp['percent'] = int(say[say.find(' ') + 1 : ]) / 100
                print(resp['percent'])
                return JsonResponse({'result': resp})
        elif key == 'Space':
            action = getGestureAction()
            print("Gesture returned - ", action)
            if action == 'play_pause':
                resp = generateResponse('play_pause')
                print("returning for play pause")
                return JsonResponse({'result': resp})
            elif action == 'next':
                resp = generateResponse('next')
                return JsonResponse({'result': resp})
            elif action == 'previous':
                resp = generateResponse('previous')
                return JsonResponse({'result': resp})
