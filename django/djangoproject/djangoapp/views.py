import requests
import uuid
from django.db.models import Count
from django.shortcuts import render, redirect
from .models import Play, PlaySession

# Create your views here.

FLASK_URL = "http://127.0.0.1:5000"

def get_session_id(request):
    if "session_id" not in request.session:
        request.session["session_id"] = str(uuid.uuid4())
    return request.session["session_id"]


def story_list(request):
    r = requests.get(f"{FLASK_URL}/stories?status=published")
    stories = r.json()
    return render(request, "game/story_list.html", {"stories": stories})


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
    r = requests.get(f"{FLASK_URL}/stories/{story_id}/start")
    start_page_id = r.json()["start_page_id"]
    return redirect("play_page", page_id=start_page_id)


def story_edit(request, story_id):
    # GET: fetch story from Flask API
    if request.method == "GET":
        r = requests.get(f"{FLASK_URL}/stories/{story_id}")
        if r.status_code != 200:
            return render(request, "game/error.html", {"message": "Story not found"})
        story = r.json()
        return render(request, "game/story_form.html", {"story": story})

    # POST: update story via Flask API
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description", "")
        status = request.POST.get("status", "published")

        r = requests.put(
            f"{FLASK_URL}/stories/{story_id}",
            json={
                "title": title,
                "description": description,
                "status": status
            }
        )
        if r.status_code == 200:
            return redirect("story_list")
        else:
            error = r.json().get("error", "Unknown error")
            return render(request, "game/story_form.html", {"story": {"id": story_id, "title": title, "description": description, "status": status}, "error": error})


def story_delete(request, story_id):
    if request.method == "POST":
        r = requests.delete(f"{FLASK_URL}/stories/{story_id}")
        # Optional: check r.status_code
    return redirect("story_list")


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