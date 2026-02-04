from django.db import models

# Create your models here.
class Play(models.Model):
    story_id = models.IntegerField()
    ending_page_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class PlaySession(models.Model):
    session_id = models.CharField(max_length=100)
    story_id = models.IntegerField()
    current_page_id = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)