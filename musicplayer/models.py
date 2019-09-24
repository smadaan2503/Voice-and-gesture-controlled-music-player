from django.db import models

# Create your models here.
class SongsData(models.Model):
    Name = models.CharField(max_length = 100)
    Singer = models.CharField(max_length = 100)
    Lyrics = models.TextField()
    Audio = models.FileField(upload_to = 'musics/')
    Thumbnail = models.ImageField(upload_to = 'thumbnails/')
    Category = models.CharField(max_length = 100)