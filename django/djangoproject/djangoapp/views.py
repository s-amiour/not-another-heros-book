from django.shortcuts import render, redirect
from django.db.models import Count
import uuid
from .models import Play, PlaySession
from .forms import StoryForm
from .services import (
    get_all_stories, get_story, create_story, update_story,
    delete_story, get_page_content, get_start_page_id
)


def get_session_id(request):
    if "session_id" not in request.session:
        request.session["session_id"] = str(uuid.uuid4())
    return request.session["session_id"]

#############  Story CRUD  #############

# --- READ ---
def story_list(request):
    stories = get_all_stories() # Fetches from Flask
    return render(request, 'game/story_list.html', {'stories': stories})


# --- CREATE ---
def story_create(request):
    if request.method == 'POST':
        form = StoryForm(request.POST)
        if form.is_valid():
            if create_story(form.cleaned_data):
                return redirect('story_list')
    else:
        form = StoryForm()
    return render(request, 'game/story_form.html', {'form': form, 'title': 'Create Story'})


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
        
    return render(request, 'game/story_form.html', {'form': form, 'title': 'Edit Story'})


# --- DELETE ---
def story_delete(request, story_id):
    if request.method == "POST":
        delete_story(story_id)
    return redirect('story_list')

########################################



def start_story(request, story_id):
    r = requests.get(f"{FLASK_URL}/stories/{story_id}/start")
    start_page_id = r.json()["start_page_id"]
    return redirect("play_page", page_id=start_page_id)


def play_page(request, page_id):
    # Get page info from Flask API
    r = requests.get(f"{FLASK_URL}/pages/{page_id}")
    page = r.json()

    # Determine if this is a preview (draft) mode
    preview = request.GET.get("preview") == "1"

    # Auto-save progress (PlaySession)
    session_id = get_session_id(request)
    PlaySession.objects.update_or_create(
        session_id=session_id,
        story_id=page["story_id"],
        defaults={"current_page_id": page_id}
    )

    # If it's an ending page AND not preview, record the play
    if page["is_ending"] and not preview:
        Play.objects.create(
            story_id=page["story_id"],
            ending_page_id=page_id
        )
        return render(request, "game/ending.html", {"page": page})

    # Normal page display
    return render(request, "game/play.html", {"page": page, "preview": preview})


def resume_story(request, story_id):
    session_id = request.session.get("session_id")
    if not session_id:
        return redirect("story_list")
    
    session = PlaySession.objects.filter(
        session_id = session_id,
        story_id = story_id
    ).first()

    if session:
        return redirect("play_page", page_id=session.current_page_id)

    return redirect("start_story", story_id=story_id)


def stats_view(request, story_id):
    plays = Play.objects.filter(story_id=story_id)
    total = plays.count()
    
    endings = plays.values("ending_page_id").annotate(count=Count("id"))

    #percentage
    for e in endings:
        e["percent"] = round(e["count"] / total * 100, 1) if total else 0

    return render(request, "game/stats.html", {
        "total": total,
        "endings": endings,
        # "page": None,  # optional, only for preview
    })


def story_stats(request, story_id):
    total = Play.objects.filter(story_id=story_id).count()
    endings = (
        Play.objects.filter(story_id=story_id)
        .values("ending_page_id")
        .annotate(count=Count("id"))
    )

    for e in endings:
        e["percent"] = round((e["count"] / total) * 100, 2) if total else 0

    return render(request, "game/stats.html", {
        "total": total,
        "endings": endings
    })