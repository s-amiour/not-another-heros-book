# CRUD Service (adapts request method calls to views.py [Adapter Pattern])

import requests
from django.conf import settings 
from collections import defaultdict

API_URL = getattr(settings, 'FLASK_API_URL', 'http://localhost:5000')

##############################  Story   ##############################


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

def update_story_status(story_id, new_status):
    """
    Patches the story status via the API.
    """
    # Assuming your Flask API supports PATCH or PUT for partial updates
    # Or you can just fetch, update dict, and send back.
    payload = {"status": new_status}
    try:
        # Note the use of requests.patch here
        resp = requests.patch(f"{API_URL}/stories/{story_id}", json=payload, timeout=5)
        return resp.status_code == 200
    except requests.RequestException:
        return False

# Delete
def delete_story(story_id):
    """Send DELETE request to Flask API"""
    requests.delete(f"{API_URL}/stories/{story_id}")


def get_start_page_id(story_id):
    """Ask Flask API where the story begins"""
    resp = requests.get(f"{API_URL}/stories/{story_id}/start")
    return (resp.json().get("start_page_id") 
            if resp.status_code == 200 else None)

##############################  Page   ##############################

def create_page(story_id, data):
    resp = requests.post(f"{API_URL}/stories/{story_id}/pages", json=data)
    return resp.status_code == 201

def update_page(page_id, data):
    resp = requests.patch(f"{API_URL}/pages/{page_id}", json=data)
    return resp.status_code == 200

def delete_page(page_id):
    resp = requests.delete(f"{API_URL}/pages/{page_id}")
    return resp.status_code == 200


def get_page_content(page_id):
    """Fetch page text and choices"""
    resp = requests.get(f"{API_URL}/pages/{page_id}")
    return resp.json() if resp.status_code == 200 else None


def get_page_label(page_id):
    resp = requests.get(f"{API_URL}/pages/{page_id}")
    return (resp.json().get("ending_label") 
            if resp.status_code == 200 else f"Ending #{page_id}")

##############################  Page   ##############################

def create_choice(page_id, data):
    # data should be {"text": "...", "target_page_id": 123}
    resp = requests.post(f"{API_URL}/pages/{page_id}/choices", json=data)
    return resp.status_code == 201

def delete_choice(choice_id):
    resp = requests.delete(f"{API_URL}/choices/{choice_id}")
    return resp.status_code == 200

##############################  Validation   ##############################

import requests
from django.conf import settings

API_URL = getattr(settings, 'FLASK_API_URL', 'http://localhost:5000')

# ... (keep existing get/create functions) ...

def validate_story_for_publishing(story_id):
    errors = []
    
    try:
        resp = requests.get(f"{API_URL}/stories/{story_id}/structure", timeout=5)
        resp.raise_for_status()
    except requests.RequestException as e:
        return [f"System error: {str(e)}"]

    data = resp.json()
    # Convert pages to a dict for O(1) lookups: {page_id: page_data}
    pages_dict = {p['id']: p for p in data.get("pages", [])}
    choices = data.get("choices", [])

    # Map page_id -> list of choices
    choices_map = defaultdict(list)
    for c in choices:
        choices_map[c['page_id']].append(c)

    # CHECKS
    if not choices:
        errors.append("Story is empty (no choices found).")
        return errors

    # Calculate how many pages contain at least one choice
    # (A Set comprehension is efficient here)
    pages_with_choices = {c['page_id'] for c in choices}
    
    # Rule 1: At least one branching page
    if len(pages_with_choices) == 0:
        # Check if we actually have pages to give a better error
        if len(pages_dict) > 0:
            errors.append("Story has pages, but none of them branch. You need at least one page with choices.")
        else:
            errors.append("Story is empty (no pages found).")
            
        # Fail early because subsequent checks rely on choices existing
        return errors

    # 2. Iterate every page to validate its individual state
    for page_id, page_data in pages_dict.items():
        is_ending = page_data.get('is_ending', False)
        page_choices = choices_map.get(page_id, [])
        count = len(page_choices)

        if is_ending:
            # ENDING PAGE RULES
            if count > 0:
                errors.append(f"Page {page_id} is marked as an Ending but has {count} choices. Endings must have 0 choices.")
        else:
            # BRANCHING PAGE RULES
            if count == 0:
                # This catches the 'Dead End' scenario that the formula misses
                errors.append(f"Page {page_id} is not an Ending, but has 0 choices. It is a dead end.")
            elif count != 2:
                # Rule 2: Exactly 2 choices
                errors.append(f"Page {page_id} has {count} choices. Must have exactly 2.")

        # 3. Referential Integrity (Dangling Pointers)
        # Ensure every choice leads to a page that actually exists
        for choice in page_choices:
            next_page_id = choice.get("next_page_id")
            if next_page_id not in pages_dict:
                errors.append(f"Page {page_id} has a choice pointing to non-existent Page {next_page_id}.")

    return errors