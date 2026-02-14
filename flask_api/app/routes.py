from flask import Blueprint, request, jsonify, abort
from .extensions import db
from .models import Story, Page, Choice
import os
from functools import wraps

# Define blueprint to prevent circular imports
main_bp = Blueprint('main', __name__)

# --- SECURITY ---
# Get this from environment variable in production
API_SECRET = os.environ.get("FLASK_API_KEY", "my_super_secret_key")

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check header
        if request.headers.get('X-API-KEY') != API_SECRET:
            return jsonify({"error": "Unauthorized: Invalid API Key"}), 401
        return f(*args, **kwargs)
    return decorated_function



##############################  Story Routing   ##############################

# Get all
@main_bp.route("/stories")
def get_stories():
    status = request.args.get("status")
    author_id = request.args.get("author_id") # Filter by author

    query = Story.query

    if status:
        query = query.filter_by(status=status)
    
    # If looking for published stories, exclude suspended ones explicitly
    if status == 'published':
        query = query.filter(Story.status != 'suspended')

    if author_id:
        query = query.filter_by(author_id=author_id)

    stories = query.all()
    
    return jsonify([
        {
            "id": s.id, 
            "title": s.title, 
            "description": s.description,
            "status": s.status, 
            "author_id": s.author_id  # Return this so Django knows who owns it
        } 
        for s in stories
    ])

# Get story
@main_bp.route("/stories/<int:story_id>")
def get_story(story_id):
    story = Story.query.get_or_404(story_id)
    return jsonify({
        "id": story.id,
        "title": story.title,
        "description": story.description,
        "status": story.status,
        "start_page_id": story.start_page_id
    })

#Search story
@main_bp.route("/stories/search")
def search_stories():
    q = request.args.get("q", "")
    stories = Story.query.filter(
        Story.title.ilike(f"%{q}%"),
        Story.status == "published"
    ).all()

    return jsonify([
        {"id": s.id, "title": s.title, "description": s.description}
        for s in stories
    ])

# Get story start page
@main_bp.route("/stories/<int:story_id>/start")
def get_start_page(story_id):
    story = Story.query.get_or_404(story_id)
    if not story.start_page_id:
        return jsonify({"error": "Story has no start page"}), 404
    
    return jsonify({"start_page_id": story.start_page_id})


# Create
@main_bp.route("/stories", methods=["POST"])
@require_api_key
def create_story():
    data = request.json
    # Create Story instance
    story = Story(
        title=data["title"],
        description=data.get("description", ""),
        status=data.get("status", "published")
    )
    db.session.add(story)
    db.session.flush()  # Generate story.id immediately

    # Handle start page

    # If the user provided text, use it. Otherwise, use a default.
    initial_text = data.get("start_text", "The story begins here...")
    
    # Create Page instance
    start_page = Page(
        story_id=story.id,
        text=initial_text,
        is_ending=False
    )
    db.session.add(start_page)
    db.session.flush()  # Generates start_page.id immediately

    # Link story and page (story.start_page_id defined)
    story.start_page_id = start_page.id
    
    # Save everything at once
    db.session.commit()


    return jsonify({"id": story.id, "start_page_id": start_page.id}), 201  # basically used for standard api pinging like postman


# Update
@main_bp.route("/stories/<int:story_id>", methods=["PUT"])
@require_api_key
def update_story(story_id):
    story = Story.query.get_or_404(story_id)
    data = request.json

    story.title = data.get("title", story.title)
    story.description = data.get("description", story.description)
    story.status = data.get("status", story.status)
    story.start_page_id = data.get("start_page_id", story.start_page_id)

    try:
        db.session.commit()
        return jsonify({"message": "Story updated successfully", "id": story.id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@main_bp.route("/stories/<int:story_id>", methods=["PATCH"])
@require_api_key
def update_story_partial(story_id):
    story = Story.query.get_or_404(story_id)
    data = request.json

    # 1. Update fields ONLY if they are present in the request
    if "title" in data:
        story.title = data["title"]
        
    if "description" in data:
        story.description = data["description"]
        
    if "status" in data:
        # Optional: Add validation here if needed (e.g., only 'draft' or 'published')
        story.status = data["status"]
        
    if "start_page_id" in data:
        story.start_page_id = data["start_page_id"]

    
    try:
        db.session.commit()
        return jsonify({"message": "Story updated successfully", "id": story.id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Delete
@main_bp.route("/stories/<int:story_id>", methods=["DELETE"])
@require_api_key
def delete_story(story_id):
    story = Story.query.get_or_404(story_id)
    db.session.delete(story)
    db.session.commit()
    return jsonify({"message": "Story deleted"})

##############################  Page Routing   ##############################

# Get
@main_bp.route("/pages/<int:page_id>")
def get_page(page_id):
    page = Page.query.get_or_404(page_id)
    choices = Choice.query.filter_by(page_id=page.id).all()
    story = page.story    

    return jsonify({
        "id": page.id,
        "story_id": story.id,
        "story_status": story.status,
        "text": page.text,
        "is_ending": page.is_ending,
        "ending_label": page.ending_label,
        "choices": [
            {"id": c.id, "text": c.text, "next_page_id": c.next_page_id}
            for c in choices
        ]
    })

# Update (PATCH is preferred for partial updates)
@main_bp.route("/pages/<int:page_id>", methods=["PATCH"])
@require_api_key
def update_page(page_id):
    # 1. Fetch the page or return 404
    page = Page.query.get_or_404(page_id)
    data = request.json

    # 2. Update fields if they exist in the payload
    if "text" in data:
        page.text = data["text"]
    
    if "is_ending" in data:
        page.is_ending = bool(data["is_ending"])
        
        # Logic: If it's no longer an ending, clear the ending label
        if not page.is_ending:
            page.ending_label = None

    if "ending_label" in data:
        # Only set label if it's actually an ending
        if page.is_ending:
            page.ending_label = data["ending_label"]

    # 3. Commit changes
    try:
        db.session.commit()
        return jsonify({
            "message": "Page updated successfully",
            "id": page.id,
            "text": page.text,
            "is_ending": page.is_ending
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Create
@main_bp.route("/stories/<int:story_id>/pages", methods=["POST"])
@require_api_key
def create_page(story_id):
    data = request.json
    page = Page(
        story_id=story_id,
        text=data["text"],
        is_ending=data.get("is_ending", False),
        ending_label=data.get("ending_label")
    )
    db.session.add(page)
    db.session.commit()
    return jsonify({"id": page.id}), 201

# Delete
@main_bp.route("/pages/<int:page_id>", methods=["DELETE"])
@require_api_key
def delete_page(page_id):
    page = Page.query.get_or_404(page_id)
    try:
        # Note: Ensure you have cascading deletes set up in your models, 
        # otherwise choices pointing TO this page might cause errors.
        db.session.delete(page)
        db.session.commit()
        return jsonify({"message": "Page deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


##############################  Choice Routing   ##############################

# Create
@main_bp.route("/pages/<int:page_id>/choices", methods=["POST"])
@require_api_key
def create_choice(page_id):
    data = request.json
    choice = Choice(
        page_id=page_id,
        text=data["text"],
        next_page_id=data["next_page_id"]
    )
    db.session.add(choice)
    db.session.commit()
    return jsonify({"id": choice.id}), 201

# Delete
@main_bp.route("/choices/<int:choice_id>", methods=["DELETE"])
@require_api_key
def delete_choice(choice_id):
    choice = Choice.query.get_or_404(choice_id)
    db.session.delete(choice)
    db.session.commit()
    return jsonify({"message": "Choice deleted"})

##############################  Validation   ##############################


@main_bp.route("/stories/<int:story_id>/structure")
def get_story_structure(story_id):
    pages = Page.query.filter_by(story_id=story_id).all()  # All pages of story
    # Get all choices for these pages
    page_ids = [p.id for p in pages]
    choices = Choice.query.filter(Choice.page_id.in_(page_ids)).all()
    
    return jsonify({
        "pages": [{"id": p.id, "story_id": p.story_id, "text": p.text, "is_ending": p.is_ending, "ending_label": p.ending_label} for p in pages],
        "choices": [{"id": c.id, "page_id": c.page_id, "text": c.text, "next_page_id": c.next_page_id} for c in choices]
    })