from django.shortcuts import render, redirect
from django.db.models import Count
from django.urls import reverse
import uuid
from .models import Play, PlaySession
from .forms import StoryForm
from .services import (
    get_all_stories, get_story, create_story, update_story,
    delete_story, get_page_content, get_start_page_id, get_page_label
)


#>> Note: The context argument property string is so important; without it, the templates won't display properly
#>> Sultan: commented out get_session_id() and resume_paeg() for now, uncomment once level13

def get_session_id(request):
    if "session_id" not in request.session:
        request.session["session_id"] = str(uuid.uuid4())
    return request.session["session_id"]


#############  Story CRUD  #############

# --- READ ---

def story_list(request):
    stories = get_all_stories()  # Fetch all stories from Flask
    query = request.GET.get("q", "").strip().lower()  # Search query

    # Filter only published stories
    stories = [s for s in stories if s.get("status") == "published"]

    if query:
        # Filter by title (case-insensitive)
        stories = [s for s in stories if query in s.get("title", "").lower()]

    return render(request, 'game/story_list.html', {
        'stories': stories,
        'search_query': request.GET.get("q", "")
    })


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




def story_create(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description", "")
        status = request.POST.get("status", "published")

        # Call Flask API to create the story
        response = requests.post(
            f"{FLASK_URL}/stories",
            json={
                "title": title,
                "description": description,
                "status": status
            }
        )
        if response.status_code == 201:
            return redirect("story_list")  # back to story list after creation
        else:
            error = response.json().get("error", "Unknown error")
            return render(request, "game/story_form.html", {"error": error})

    # GET request: show empty form
    return render(request, "game/story_form.html")


def start_story(request, story_id):
    """
    Redirects the user to the first page of a story.
    Handles preview mode (for draft stories) without recording stats.
    """
    
    # Get the first page ID from Flask
    start_page_id = get_start_page_id(story_id)
    
    # Check if the story actually has a start page
    if not start_page_id:
        # If no start page, send user back to story list
        return redirect("story_list")
    
    # Check if this is a draft preview
    preview = request.GET.get("preview")

    # Build the URL for the play_page view
    # reverse() generates the URL from the view name and kwargs
    url = reverse(
        "play_page",  # view name in urls.py
        kwargs={"story_id": story_id, "page_id": start_page_id}  # dynamic parts of URL
    )
    
    if preview:
        url += "?preview=1"  # append query string

    # Return a proper HttpResponseRedirect
    # redirect() takes a string URL and returns an HttpResponseRedirect
    # Do NOT use + on redirect() itself; that causes the TypeError
    return redirect(url)



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

    session_id = get_session_id(request)

    # save / update session
    PlaySession.objects.update_or_create(
        session_id=session_id,
        story_id=story_id,
        defaults={"current_page_id": page_id}
    )

    # Play page will skip stats if preview
    preview = request.GET.get("preview")

    # Record the play if ending reached
    if page_content.get("is_ending") and not preview:
        Play.objects.create(
            story_id=story_id,
            ending_page_id=page_id
        )

        PlaySession.objects.filter(
            session_id=session_id,
            story_id=story_id
        ).delete()

    # render game ui
    return render(request, "game/play.html", {
        "story_id": story_id,
        "page": page_content
    })

def resume_story(request, story_id):
    session_id = request.session.get("session_id")
    if not session_id:
        return redirect("start_story", story_id=story_id)

    session = PlaySession.objects.filter(
        session_id=session_id,
        story_id=story_id
    ).first()

    if session:
        return redirect("play_page", story_id=story_id, page_id=session.current_page_id)

#     return redirect("start_story", story_id=story_id)


# View Statistics
def stats_view(request, story_id):
    plays = Play.objects.filter(story_id=story_id)
    total = plays.count()
    

    
    endings = plays.values("ending_page_id").annotate(count=Count("id"))

    #percentage
    for e in endings:

        e["percent"] = round(e["count"] / total * 100, 2) if total else 0
        e["label"] = get_page_label(e["ending_page_id"])

    return render(request, "game/stats.html", {
        "total": total,
        "endings": endings,
        # "page": None,  # optional, only for preview

    })


def author_story_list(request):
    stories = get_all_stories()  # no filter
    return render(request, "game/author_list.html", {"stories": stories})