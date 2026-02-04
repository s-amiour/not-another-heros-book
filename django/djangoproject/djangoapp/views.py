import requests
from django.shortcuts import render, redirect
from .models import Play

# Create your views here.

FLASK_URL = "http://127.0.0.1:5000"

def story_list(request):
    r = requests.get(f"{FLASK_URL}/stories?status=published")
    stories = r.json()
    return render(request, "game/story_list.html", {"stories": stories})

def start_story(request, story_id):
    r = requests.get(f"{FLASK_URL}/stories/{story_id}/start")
    start_page_id = r.json()["start_page_id"]
    return redirect("play_page", page_id=start_page_id)

def play_page(request, page_id):
    r = requests.get(f"{FLASK_URL}/pages/{page_id}")
    page = r.json()

    if page["is_ending"]:
        Play.objects.create(
            story_id=page_id,
            ending_page_id=page_id
        )
        return render(request, "game/ending.html", {"page": page})

    return render(request, "game/play.html", {"page": page})

