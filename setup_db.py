from app import app, db, UserProfile, Memory, DateIdea

# Ensure we are in app context
with app.app_context():
    db.create_all()

    # Default profile
    if not UserProfile.query.first():
        db.session.add(UserProfile(
            name="Your Name",
            anniversary="2025-10-13",         # Example wedding/engagement date
            relationship_start="2024-09-13", # Example relationship start
            bio="This is a short bio about us!",
            profile_pic=None
        ))
    

    # Default memories
    if not Memory.query.first():
        memories = [
            "Our first coffee date at 'The Cozy Bean' - I loved hearing about your passion for books.",
            "That rainy afternoon walk when we shared my umbrella and just talked for hours.",
            "The way you laughed when I told that silly joke – it instantly brightened my day.",
            "Our first movie night in, cuddling on the couch. Simple but perfect.",
            "Every moment since we met has been a beautiful new memory. Happy Anniversary, my love!"
        ]
        for mem in memories:
            db.session.add(Memory(content=mem))

    # Default date ideas
    if not DateIdea.query.first():
        ideas = [
            "A picnic in the park at sunset.",
            "Try that new Italian restaurant we talked about.",
            "Have a baking competition – who can make the best cupcakes?",
            "Visit a local art gallery or museum.",
            "Go stargazing away from the city lights.",
            "A cozy night in with a movie marathon and homemade popcorn."
        ]
        for idea in ideas:
            db.session.add(DateIdea(idea=idea))

    db.session.commit()
    print("Database initialized successfully.")
