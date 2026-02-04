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


def start_story(request, story_id):
    r = requests.get(f"{FLASK_URL}/stories/{story_id}/start")
    start_page_id = r.json()["start_page_id"]
    return redirect("play_page", page_id=start_page_id)


def play_page(request, page_id):
    #Get page from Flask
    r = requests.get(f"{FLASK_URL}/pages/{page_id}")
    page = r.json()

    #Auto-save progress (anonymous)
    session_id = get_session_id(request)
    PlaySession.objects.update_or_create(
        session_id=session_id,
        story_id=page.get("story_id", page_id),  # use real story_id if Flask provides it
        defaults={"current_page_id": page_id}
    )

    #If page is an ending
    if page["is_ending"]:
        story_status = page.get("story_status", "published")  # must include in Flask response
        # Only save Play if story is published
        if story_status != "draft":
            Play.objects.create(
                story_id=page.get("story_id", page_id),  # replace page_id with real story_id
                ending_page_id=page_id
            )
        return render(request, "game/ending.html", {"page": page})

    #Regular page rendering
    return render(request, "game/play.html", {"page": page})


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