from django.db import models
from django.contrib.auth.models import User

class Play(models.Model):
    # Store the ID of the story/ending from Flask
    story_id = models.IntegerField(help_text="The ID of the story played (from Flask)")
    ending_page_id = models.IntegerField(help_text="The ID of the final page reached (from Flask)")
    
    # Track when it happened
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='plays')

    def __str__(self):
        return f"Story {self.story_id} finished at {self.created_at}"

class PlaySession(models.Model):
    session_id = models.CharField(max_length=100)
    story_id = models.IntegerField()
    current_page_id = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)