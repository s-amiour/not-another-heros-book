from django.shortcuts import render, redirect
from django.db.models import Count
from django.urls import reverse
from django.contrib import messages  # Messages to client
from django.views.decorators.http import require_POST
from django.conf import settings 
import uuid
import requests
from .models import Play, PlaySession
from .forms import StoryForm, PageForm, ChoiceForm
from .services import (
    get_all_stories, get_story, create_story, update_story,
    delete_story, get_page_content, get_start_page_id, get_page_label,
    validate_story_for_publishing, update_story_status, create_page, update_page, delete_page, create_choice, delete_choice,
)


API_URL = getattr(settings, 'FLASK_API_URL', 'http://localhost:5000')

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
    
    # Get current session ID
    session_id = get_session_id(request)

    # For each story, check if there's a saved PlaySession
    for s in stories:
        s["has_progress"] = PlaySession.objects.filter(
            session_id=session_id,
            story_id=s["id"]
        ).exists()

    return render(request, 'game/story_list.html', {
        'stories': stories,
        'search_query': request.GET.get("q", "")
    })

def author_story_list(request):
    stories = get_all_stories()  # no filter
    return render(request, "game/author_list.html", {"stories": stories})

# --- CREATE ---
def story_create(request):
    # Submitted form
    if request.method == 'POST':
        form = StoryForm(request.POST)  # Constructor; 
        if form.is_valid():
            story_data = form.cleaned_data
            # FORCE DRAFT
            story_data['status'] = 'draft'

            if create_story(story_data):  # .cleaned_data (Input Sanitization Wall #2) #1:API SQLAlchemy in flaskapi prepares and executes
                messages.success(request, "Story draft created! Now add your pages.")  # Action Informer
                return redirect('author_story_list')
        else:
            messages.error(request, "Error creating story. Please check the form below")  # Action Informer
    else:
        # Empty form
        form = StoryForm()
    return render(request, 'game/story_form.html', {'story': form})





@require_POST  # Security: Prevent publishing via a random link click
def story_publish(request, story_id):
    # 1. Run the Gatekeeper
    errors = validate_story_for_publishing(story_id)
    
    if errors:
        # Validation Failed
        messages.error(request, "Publishing Failed:")
        for e in errors:
            messages.error(request, f"• {e}")
    else:
        # Validation Passed: Update Status
        # (You might need to add update_story_status to your services.py)
        update_story_status(story_id, "published")
        messages.success(request, "Story successfully published! It is now live.")
        
    # Always redirect back to the author dashboard
    return redirect('author_story_list')

# --- UNPUBLISH ACTION ---
@require_POST
def story_unpublish(request, story_id):
    """
    Reverts a story to 'draft' status so it can be edited.
    """
    # 1. Update status via API
    success = update_story_status(story_id, "draft")
    
    if success:
        messages.warning(request, "Story is now unpublished (Draft). It is hidden from players, but you can edit it.")
    else:
        messages.error(request, "System error: Could not unpublish story.")
        
    return redirect('author_story_list')






# --- UPDATE ---
def story_edit(request, story_id):
    story_data = get_story(story_id)  # Fetch existing data
    if not story_data:
        messages.error(request, "Story not found.")
        return redirect('author_story_list')
        
    # 2. Prevent editing if Published
    if story_data.get('status') == 'published':
        messages.error(request, "⚠️ You cannot edit a live story. Please 'Unpublish' it first.")
        return redirect('author_story_list')
    
    if request.method == 'POST':
        form = StoryForm(request.POST)
        if form.is_valid():
            clean_data = form.cleaned_data
            
            # SAFETY LOCK: 
            # We overwrite the form's status with the EXISTING database status.
            # This ensures 'story_edit' can NEVER change a story's status.
            # Status changes are now the exclusive job of 'story_publish'.
            clean_data['status'] = story_data['status']

            # Send update to API
            if update_story(story_id, clean_data):
                messages.success(request, "Story details updated successfully.")
                return redirect('author_story_list')
            else:
                messages.error(request, "System error: Could not save changes.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        # Pre-fill
        form = StoryForm(initial=story_data)
        
    return render(request, 'game/story_form.html', {
        'story': form, 
        'edit_as_title': True,
        'current_status': story_data.get('status')  # Pass current status for UI logic
    })


# --- DELETE ---
def story_delete(request, story_id):
    if request.method == "POST":
        messages.success(request, "Story deleted successfully!")  # Action Informer
        delete_story(story_id)
    return redirect('author_story_list')

#############  Gameplay  #############

def start_story(request, story_id):
    """
    Redirects the user to the first page of a story.
    Handles preview mode (for draft stories) without recording stats.
    """
    
    start_page_id = get_start_page_id(story_id)
    
    # Check if the story actually has a start page
    if not start_page_id:
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
        "page": page_content,
        "preview": preview
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
    return redirect("start_story", story_id=story_id)

#############  View Statistics  #############

def stats_view(request, story_id):
    plays = Play.objects.filter(story_id=story_id)
    total = plays.count()
    
    endings = plays.values("ending_page_id").annotate(count=Count("id"))

    for e in endings:
        #percentage
        e["percent"] = round(e["count"] / total * 100, 2) if total else 0
        #ending label
        e["label"] = get_page_label(e["ending_page_id"])

    return render(request, "game/stats.html", {
        "total": total,
        "endings": endings,
        # "page": None,  # optional, only for preview
    })


##############################  Builder   ##############################


# --- STRUCTURE DASHBOARD ---
def story_structure(request, story_id):
    """
    Lists all pages and acts as the 'Builder' home.
    """
    # Reuse your existing validation logic to fetch the full structure (Pages + Choices)
    # Or just fetch pages if you have a specific endpoint. 
    # Let's assume we use the structure endpoint which returns everything.
    try:
        resp = requests.get(f"{API_URL}/stories/{story_id}/structure")
        data = resp.json()
    except:
        messages.error(request, "Could not load story structure.")
        return redirect('author_story_list')

    pages = data.get('pages', [])
    # Mark the start page visually
    start_page_id = get_start_page_id(story_id)

    return render(request, 'game/builder/structure.html', {
        'story_id': story_id,
        'pages': pages,
        'start_page_id': start_page_id,
        'story_title': data.get('title', 'Story')  # Assuming structure returns metadata too
    })


# --- PAGE CRUD ---

def page_create_view(request, story_id):
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if create_page(story_id, form.cleaned_data):
                messages.success(request, "Page created!")
                return redirect('story_structure', story_id=story_id)
    else:
        form = PageForm()
    
    return render(request, 'game/builder/page_form.html', {
        'form': form, 'story_id': story_id, 'is_create': True
    })

def page_edit_view(request, story_id, page_id):
    """
    Complex view: Handles updating Page Text AND Adding Choices
    """
    # 1. Fetch Page Data
    page_content = get_page_content(page_id) # Returns {id, text, is_ending, choices: []}
    if not page_content:
        return redirect('story_structure', story_id=story_id)

    # 2. Fetch All Pages (for the Choice Target Dropdown)
    # We need a list of tuples: [(id, "id - snippet"), ...]
    struct_resp = requests.get(f"{API_URL}/stories/{story_id}/structure").json()
    all_pages = struct_resp.get('pages', [])
    
    # Exclude current page from targets (prevent self-loops if you want, though valid in some games)
    # Creating the options list:
    page_options = [
        (p['id'], f"Page {p['id']}: {p['text'][:30]}...") 
        for p in all_pages if p['id'] != page_id
    ]

    #Initialize Forms as None
    p_form = None
    c_form = None

    # 3. Handle Forms
    if request.method == 'POST':
        
        if 'update_page' in request.POST:
            p_form = PageForm(request.POST) # Bind user input
            c_form = ChoiceForm(page_options=page_options) # Empty choice form
            
            if p_form.is_valid():
                # Send to API
                success = update_page(page_id, p_form.cleaned_data)
                if success:
                    messages.success(request, "Page content updated.")
                    # Redirect to avoid "Confirm Resubmission" on refresh
                    return redirect('page_edit', story_id=story_id, page_id=page_id)
                else:
                    messages.error(request, "API Error: Could not save page.")
            else:
                messages.error(request, "Please correct the errors in the page form.")

        # --- CASE B: Add Choice ---
        elif 'add_choice' in request.POST:
            c_form = ChoiceForm(page_options, request.POST) # Bind user input
            # Load existing page text so the top form isn't empty if choice fails
            p_form = PageForm(initial={'text': page_content['text'], 'is_ending': page_content['is_ending']})
            
            if c_form.is_valid():
                success = create_choice(page_id, c_form.cleaned_data)
                if success:
                    messages.success(request, "Choice added.")
                    return redirect('page_edit', story_id=story_id, page_id=page_id)
                else:
                    messages.error(request, "API Error: Could not add choice.")
            else:
                messages.error(request, "Error adding choice.")

    # GET Request: Initialize forms
    # Only load from DB if forms weren't already created in the POST block above
    if not p_form:
        p_form = PageForm(initial={
            'text': page_content.get('text', ''), 
            'is_ending': page_content.get('is_ending', False)
        })
    
    if not c_form:
        c_form = ChoiceForm(page_options=page_options)

    return render(request, 'game/builder/page_detail.html', {
        'story_id': story_id,
        'page': page_content,
        'p_form': p_form,
        'c_form': c_form
    })

@require_POST
def page_delete_view(request, story_id, page_id):
    delete_page(page_id)
    messages.success(request, "Page deleted.")
    return redirect('story_structure', story_id=story_id)

@require_POST
def choice_delete_view(request, story_id, page_id, choice_id):
    delete_choice(choice_id)
    messages.success(request, "Choice removed.")
    return redirect('page_edit', story_id=story_id, page_id=page_id)