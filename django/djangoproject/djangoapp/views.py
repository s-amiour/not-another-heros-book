from django.shortcuts import render, redirect
from django.db.models import Count
import uuid
from .models import Play, PlaySession
from .forms import StoryForm
from .services import (
    get_all_stories, get_story, create_story, update_story,
    delete_story, get_page_content, get_start_page_id
)

#>> Note: The context argument property string is so important; without it, the templates won't display properly
#>> Sultan: commented out get_session_id() and resume_paeg() for now, uncomment once level13

# def get_session_id(request):
#     if "session_id" not in request.session:
#         request.session["session_id"] = str(uuid.uuid4())
#     return request.session["session_id"]

#############  Story CRUD  #############

# --- READ ---
def story_list(request):
    stories = get_all_stories()  # Fetches from Flask
    return render(request, 'game/story_list.html', {'stories': stories})


# --- CREATE ---
def story_create(request):
    # Submitted form
    if request.method == 'POST':
        form = StoryForm(request.POST)  # Constructor; 
        if form.is_valid():
            if create_story(form.cleaned_data):
                return redirect('story_list')
    else:
        # Empty form
        form = StoryForm()
    return render(request, 'game/story_form.html', {'story': form})


# --- UPDATE ---
def story_edit(request, story_id):
    story_data = get_story(story_id)  # Fetch existing data
    if not story_data:
        return redirect('story_list')
        
    if request.method == 'POST':
        form = StoryForm(request.POST)
        if form.is_valid():
            if update_story(story_id, form.cleaned_data):
                return redirect('story_list')
    else:
        # Pre-fill
        form = StoryForm(initial=story_data)
        
    return render(request, 'game/story_form.html', {'story': form, 'edit_as_title': 'true'})


# --- DELETE ---
def story_delete(request, story_id):
    if request.method == "POST":
        delete_story(story_id)
    return redirect('story_list')

########################################



def start_story(request, story_id):
    """Redirect browser to the play_page for that ID."""
    start_page_id = get_start_page_id(story_id)
    
    if start_page_id:
        # Redirect to the actual game page
        return redirect("play_page", story_id=story_id, page_id=start_page_id)
    else:
        # Error handling: Story has no pages yet
        return redirect("story_list")


def play_page(request, story_id, page_id):
    """
    1. Fetches page content (text + choices) from Flask.
    2. Checks if it is an ENDING.
    3. If ending -> Save stats to Django DB.
    """
    # A. Fetch Content
    page_content = get_page_content(page_id)
    
    if not page_content:
        return render(request, "game/error.html", {"message": "Page not found"})

    # Record the play if ending reached
    if page_content.get("is_ending"):
        # Save to Django database (anonymous play)
        Play.objects.create(
            story_id=story_id,
            ending_page_id=page_id
        )

    # render game ui
    return render(request, "game/play.html", {
        "story_id": story_id,
        "page": page_content
    })


# def resume_story(request, story_id):
#     session_id = request.session.get("session_id")
#     if not session_id:
#         return redirect("story_list")
    
#     session = PlaySession.objects.filter(
#         session_id = session_id,
#         story_id = story_id
#     ).first()

#     if session:
#         return redirect("play_page", page_id=session.current_page_id)

#     return redirect("start_story", story_id=story_id)



# View Statistics
def stats_view(request, story_id):
    plays = Play.objects.filter(story_id=story_id)
    total = plays.count()
    
    
    endings = plays.values("ending_page_id").annotate(count=Count("id"))

    for e in endings:
        #percentage
        e["percent"] = round(e["count"] / total * 100, 2) if total else 0
        #ending label
        e["ending_label"] = get_page_content(e["ending_page_id"])["ending_label"]

    return render(request, "game/stats.html", {
        "total": total,
        "endings": endings,
        # "page": None,  # optional, only for preview
    })