from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class ChatMessage(models.Model):
    msgText = models.TextField()
    msgAuthor = models.ForeignKey(User)
    msgData = models.DateTimeField(auto_now_add=True)

