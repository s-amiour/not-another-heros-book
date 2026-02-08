from django.urls import path
from . import views

# Third param is used as named as variable name to be used in templates. this variables per se identifies the urlpattern in urlpatterns
urlpatterns = [
    path("", views.story_list, name="story_list"),
    path("stories/create/", views.story_create, name="story_create"),
    path("stories/<int:story_id>/edit/", views.story_edit, name="story_edit"),
    path("stories/<int:story_id>/delete/", views.story_delete, name="story_delete"),

    # Gameplay
    path("play/<int:page_id>/", views.play_page, name="story_play"),

    path("stats/<int:story_id>/", views.stats_view, name="stats"),
]
