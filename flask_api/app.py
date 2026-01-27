from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from models import db, Story, Page, Choice

# Create WSGI app instance
app = Flask(__name__)
# Config purposes
app.config.from_object(Config)
# Bind app to db obj, maintaining Application Factory pattern
db.init_app(app)
# Allow communication between frontend and backend
CORS(app)

# Create DB
with app.app_context():
    db.create_all()

##############################  Story Routing   ##############################

# Get all
@app.route("/stories")
def get_stories():
    status = request.args.get("status")
    if status:
        stories = Story.query.filter_by(status=status).all()
    else:
        stories = Story.query.all()

    return jsonify([
        {"id": s.id, "title": s.title, "description": s.description}
        for s in stories
    ])

# Get story
@app.route("/stories/<int:story_id>")
def get_story(story_id):
    story = Story.query.get_or_404(story_id)
    return jsonify({
        "id": story.id,
        "title": story.title,
        "description": story.description,
        "start_page_id": story.start_page_id
    })

# Get story start page
@app.route("/stories/<int:story_id>/start")
def get_start_page(story_id):
    story = Story.query.get_or_404(story_id)
    if not story.start_page_id:
        return jsonify({"error": "Story has no start page"}), 404
    
    return jsonify({"start_page_id": story.start_page_id})


# Create
@app.route("/stories", methods=["POST"])
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
@app.route("/stories/<int:story_id>", methods=["PUT"])
def update_story(story_id):
    story = Story.query.get_or_404(story_id)
    data = request.json

    story.title = data.get("title", story.title)
    story.description = data.get("description", story.description)
    story.status = data.get("status", story.status)
    story.start_page_id = data.get("start_page_id", story.start_page_id)

    db.session.commit()
    return jsonify({"message": "Story updated"})


# Delete
@app.route("/stories/<int:story_id>", methods=["DELETE"])
def delete_story(story_id):
    story = Story.query.get_or_404(story_id)
    db.session.delete(story)
    db.session.commit()
    return jsonify({"message": "Story deleted"})

##############################  Page Routing   ##############################

# Get
@app.route("/pages/<int:page_id>")
def get_page(page_id):
    page = Page.query.get_or_404(page_id)
    choices = Choice.query.filter_by(page_id=page.id).all()

    return jsonify({
        "id": page.id,
        "text": page.text,
        "is_ending": page.is_ending,
        "ending_label": page.ending_label,
        "choices": [
            {"id": c.id, "text": c.text, "next_page_id": c.next_page_id}
            for c in choices
        ]
    })


# Create
@app.route("/stories/<int:story_id>/pages", methods=["POST"])
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

@app.route("/pages/<int:page_id>/choices", methods=["POST"])
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

if __name__ == "__main__":
    app.run(debug=True)
