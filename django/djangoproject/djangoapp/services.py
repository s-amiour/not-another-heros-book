# CRUD Service (adapts request method calls to views.py [Adapter Pattern])

import requests
from django.conf import settings 

API_URL = getattr(settings, 'FLASK_API_URL', 'http://localhost:5000')

# Get all
def get_all_stories(status=None):
    """Fetch list of stories from Flask"""
    params = {'status': status} if status else {}
    try:
        response = requests.get(f"{API_URL}/stories", params=params)
        return response.json() if response.status_code == 200 else []
    except requests.exceptions.RequestException:
        return []

# Get <id>
def get_story(story_id):
    """Fetch a single story metadata"""
    resp = requests.get(f"{API_URL}/stories/{story_id}")
    return resp.json() if resp.status_code == 200 else None

# Create
def create_story(data):
    """Send POST request to Flask API to create a story"""
    resp = requests.post(f"{API_URL}/stories", json=data)
    return resp.status_code == 201

# Update
def update_story(story_id, data):
    """Send PUT request to update story"""
    resp = requests.put(f"{API_URL}/stories/{story_id}", json=data)
    return resp.status_code == 200

# Delete
def delete_story(story_id):
    """Send DELETE request to Flask API"""
    requests.delete(f"{API_URL}/stories/{story_id}")


def get_page_content(page_id):
    """Fetch page text and choices"""
    resp = requests.get(f"{API_URL}/pages/{page_id}")
    return resp.json() if resp.status_code == 200 else None

def get_start_page_id(story_id):
    """Ask Flask API where the story begins"""
    resp = requests.get(f"{API_URL}/stories/{story_id}/start")
    return (resp.json().get("start_page_id") 
            if resp.status_code == 200 else None)