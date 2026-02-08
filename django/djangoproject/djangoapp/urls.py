from django.urls import path
from . import views

# Third param is used as named as variable name to be used in templates. this variables per se identifies the urlpattern in urlpatterns
urlpatterns = [
    # CRUD paths
    path("", views.story_list, name="story_list"),
    path("stories/create/", views.story_create, name="story_create"),
    path("stories/<int:story_id>/edit/", views.story_edit, name="story_edit"),
    path("stories/<int:story_id>/delete/", views.story_delete, name="story_delete"),

    # - Gameplay Routes -
    # Entry point (finds the start page -> Redirects)
    path("stories/<int:story_id>/start/", views.start_story, name="start_story"),
    
    # Game engine (displays a specific page)
    # keep story_id in the URL so we can save it to the DB when the game ends
    # path("play/<int:page_id>/", views.play_page, name="story_play"),
    path("stories/<int:story_id>/play/<int:page_id>/", views.play_page, name="play_page"),

    # Stats
    path("stats/<int:story_id>/", views.stats_view, name="stats"),
]
