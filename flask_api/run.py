from app import create_app
from app.extensions import db
from app.models import Story, Page, Choice

app = create_app()

def seed_database():
    """Populates the database with initial data."""
    
    # Check if data exists to prevent duplicates (optional)
    if Story.query.first():
        print("Database already contains data. Skipping seed.")
        return

    print("Seeding database...")

    # --- STORIES ---
    # We set IDs explicitly to match mock data structure
    story1 = Story(
        id=1,
        title="The Haunted Mansion",
        description="Explore a mysterious mansion and uncover its secrets",
        status="published",
        start_page_id=1
    )
    story2 = Story(
        id=2,
        title="Space Adventure",
        description="Journey through the cosmos",
        status="published",
        start_page_id=4
    )

    # --- PAGES ---
    pages = [
        # Story 1:* Pages
        Page(
            id=1, story_id=1, 
            text="You stand before a dark, ominous mansion. The front door is slightly ajar. What do you do?",
            is_ending=False, ending_label=None
        ),
        Page(
            id=2, story_id=1, 
            text="You enter the mansion. The door slams shut behind you. You survived... or did you?",
            is_ending=True, ending_label="Trapped Inside"
        ),
        Page(
            id=3, story_id=1, 
            text="You walk away. Sometimes the best adventure is the one you don't have.",
            is_ending=True, ending_label="Escaped Safely"
        ),
        # Story 2 Pages
        Page(
            id=4, story_id=2, 
            text="Your spaceship is ready. Do you explore the asteroid field or head to the planet?",
            is_ending=False, ending_label=None
        ),
        Page(
            id=5, story_id=2, 
            text="You discover rare minerals! You're now rich beyond your wildest dreams!",
            is_ending=True, ending_label="Wealthy Explorer"
        ),
        Page(
            id=6, story_id=2, 
            text="You meet friendly aliens who share their technology. Humanity is saved!",
            is_ending=True, ending_label="Hero of Earth"
        ),
    ]

    # --- CHOICES ---
    choices = [
        Choice(id=1, page_id=1, text="Enter the mansion", next_page_id=2),
        Choice(id=2, page_id=1, text="Walk away", next_page_id=3),
        Choice(id=3, page_id=4, text="Explore the asteroid field", next_page_id=5),
        Choice(id=4, page_id=4, text="Head to the planet", next_page_id=6),
    ]

    # --- COMMIT ---
    # Add everything to the session
    db.session.add(story1)
    db.session.add(story2)
    db.session.add_all(pages)
    db.session.add_all(choices)

    # Commit the transaction
    db.session.commit()
    print("Database seeded successfully!")

if __name__ == "__main__":
    # Context is required to access the DB
    with app.app_context():
        # Team note: uncomment next line to WIPE and reset the DB every time we restart
        # db.drop_all()
        
        # Create tables if they don't exist (handled by factory in __init__.py, but safe here)
        db.create_all()
        
        # Run seed
        seed_database()

    app.run(debug=True)