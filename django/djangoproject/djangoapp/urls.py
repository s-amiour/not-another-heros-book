from django.urls import path
from . import views

urlpatterns = [
    path("", views.story_list, name="story_list"),
    path("stories/create/", views.story_create, name="story_create"),
    path("stories/<int:story_id>/edit/", views.story_edit, name="story_edit"),
    path("stories/<int:story_id>/delete/", views.story_delete, name="story_delete"),
    path("play/<int:page_id>/", views.play_page, name="play_page"),
    path("stats/<int:story_id>/", views.stats_view, name="stats"),
]
