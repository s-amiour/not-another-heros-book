from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

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

    # Resuming story
    path("stories/<int:story_id>/resume/", views.resume_story, name="resume_story"),

    # Stats
    path("stats/<int:story_id>/", views.stats_view, name="stats_view"),

    # Author
    path("author/stories/", views.author_story_list, name="author_story_list"),

    # Publish | Unpublish
    path("stories/<int:story_id>/publish/", views.story_publish, name="story_publish"),
    path('stories/<int:story_id>/unpublish/', views.story_unpublish, name='story_unpublish'),


    # --- BUILDER ---
    path("stories/<int:story_id>/builder/", views.story_structure, name="story_structure"),
    path("stories/<int:story_id>/pages/new/", views.page_create_view, name="page_create"),
    path("stories/<int:story_id>/pages/<int:page_id>/", views.page_edit_view, name="page_edit"),
    path("stories/<int:story_id>/pages/<int:page_id>/delete/", views.page_delete_view, name="page_delete"),
    
    # Choice Delete (Choice creation is handled inside page_edit)
    path("stories/<int:story_id>/pages/<int:page_id>/choices/<int:choice_id>/delete/", 
         views.choice_delete_view, name="choice_delete"),



    # --- AUTHENTICATION ---
    path('register/', views.register_view, name='register'),
    
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    
    # Logout redirects to home or login after logging out
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]
