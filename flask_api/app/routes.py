from flask import Blueprint, request, jsonify
from .extensions import db
from .models import Story, Page, Choice

# Define blueprint to prevent circular imports
main_bp = Blueprint('main', __name__)

##############################  Story Routing   ##############################

# Get all
@main_bp.route("/stories")
def get_stories():
    status = request.args.get("status")
    if status:
        stories = Story.query.filter_by(status=status).all()
    else:
        stories = Story.query.all()

    return jsonify([
        {"id": s.id, "title": s.title, "description": s.description,
         "status": s.status, "start_page_id": s.start_page_id} 
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
def create_story():
    data = request.json
    story = Story(
        title=data["title"],
        description=data.get("description", ""),
        status=data.get("status", "published")
    )
    db.session.add(story)
    db.session.commit()
    return jsonify({"id": story.id}), 201


# Update
@main_bp.route("/stories/<int:story_id>", methods=["PUT"])
def update_story(story_id):
    story = Story.query.get_or_404(story_id)
    data = request.json

    story.title = data.get("title", story.title)
    story.description = data.get("description", story.description)
    story.status = data.get("status", story.status)
    story.start_page_id = data.get("start_page_id", story.start_page_id)

    db.session.commit()  # SET
    return jsonify({"message": "Story updated"})


# Delete
@main_bp.route("/stories/<int:story_id>", methods=["DELETE"])
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


# Create
@main_bp.route("/stories/<int:story_id>/pages", methods=["POST"])
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

##############################  Choice Routing   ##############################

@main_bp.route("/pages/<int:page_id>/choices", methods=["POST"])
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
