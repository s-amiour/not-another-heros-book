from django.urls import path
from . import views

urlpatterns = [
    path("", views.story_list, name="story_list"),
    path("stories/<int:story_id>/start/", views.start_story, name="start_story"),
    path("play/<int:page_id>/", views.play_page, name="play_page"),
]
