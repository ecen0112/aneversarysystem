from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from flask_migrate import Migrate

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here'

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Upload folders
PROFILE_PIC_FOLDER = os.path.join('static', 'profile_pics')
GALLERY_FOLDER = os.path.join('static', 'gallery')
os.makedirs(PROFILE_PIC_FOLDER, exist_ok=True)
os.makedirs(GALLERY_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Admin/User passwords
CORRECT_PASSWORD = 'user_secret'
ADMIN_PASSWORD = 'admin_secret'


# ------------------ MODELS ------------------
class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    profile_pic = db.Column(db.String(150), nullable=True)
    relationship_start = db.Column(db.String(10), nullable=True)  # YYYY-MM-DD


class Memory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)


class DateIdea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idea = db.Column(db.Text)


class GalleryImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100))


# ------------------ HELPERS ------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)

    return decorated_function


# ------------------ ROUTES ------------------
@app.route('/')
def index():
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        password = request.form['password']
        if password == CORRECT_PASSWORD:
            session['logged_in'] = True
            session['role'] = 'user'
            return redirect(url_for('dashboard'))
        elif password == ADMIN_PASSWORD:
            session['logged_in'] = True
            session['role'] = 'admin'
            return redirect(url_for('dashboard'))
        else:
            error = 'Incorrect password. Please try again.'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    profile = UserProfile.query.first()

    if not profile or not profile.relationship_start:
        flash("Please set your relationship start date in the profile.", "warning")
        return redirect(url_for("profile"))

    start_date = datetime.strptime(profile.relationship_start, "%Y-%m-%d")
    today = datetime.today()

    # Calculate next anniversary
    anniv_month = start_date.month
    anniv_day = start_date.day
    next_anniv = datetime(today.year, anniv_month, anniv_day)
    if next_anniv < today:
        next_anniv = datetime(today.year + 1, anniv_month, anniv_day)

    years = today.year - start_date.year
    if (today.month, today.day) < (anniv_month, anniv_day):
        years -= 1

    days_together = (today - start_date).days

    duration = f"{years} year{'s' if years != 1 else ''} together 💕"
    days_text = f"{days_together} day{'s' if days_together != 1 else ''} since the relationship started 🌸"

    return render_template(
        "dashboard.html",
        profile=profile,
        duration=duration,
        days_text=days_text,
        relationship_start=profile.relationship_start,
        next_anniversary=next_anniv
    )


@app.route('/profile', methods=['GET', 'POST'])
@login_required
@admin_required
def profile():
    profile = UserProfile.query.first()
    if not profile:
        profile = UserProfile(name="", bio="", profile_pic=None, relationship_start=None)
        db.session.add(profile)
        db.session.commit()

    if request.method == 'POST':
        profile.name = request.form.get('name', profile.name)
        profile.relationship_start = request.form.get('relationship_start', profile.relationship_start)
        profile.bio = request.form.get('bio', profile.bio)

        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(PROFILE_PIC_FOLDER, filename))
                profile.profile_pic = filename

        if request.form.get('delete_pic') == '1' and profile.profile_pic:
            pic_path = os.path.join(PROFILE_PIC_FOLDER, profile.profile_pic)
            if os.path.exists(pic_path):
                os.remove(pic_path)
            profile.profile_pic = None

        db.session.commit()
        flash("Profile updated successfully!", "success")

    return render_template('profile.html', profile=profile)


# ----------- MEMORIES -----------
@app.route('/memories', methods=['GET', 'POST'])
@login_required
def memories():
    if request.method == 'POST' and session.get('role') == 'admin':
        new_memory = request.form.get('memory')
        if new_memory:
            db.session.add(Memory(content=new_memory))
            db.session.commit()
    all_memories = Memory.query.all()
    return render_template('memories.html', memories=all_memories)


@app.route("/edit_memory/<int:memory_id>", methods=["POST"])
@login_required
@admin_required
def edit_memory(memory_id):
    memory = Memory.query.get_or_404(memory_id)
    new_content = request.form.get("edited_memory")
    if new_content:
        memory.content = new_content
        db.session.commit()
    return redirect(url_for("memories"))


@app.route("/delete_memory/<int:memory_id>", methods=["POST"])
@login_required
@admin_required
def delete_memory(memory_id):
    memory = Memory.query.get_or_404(memory_id)
    db.session.delete(memory)
    db.session.commit()
    return redirect(url_for("memories"))


# ----------- DATE IDEAS -----------
@app.route('/date_ideas', methods=['GET', 'POST'])
@login_required
def date_ideas():
    if request.method == 'POST' and session.get('role') == 'admin':
        new_idea = request.form.get('idea')
        if new_idea:
            db.session.add(DateIdea(idea=new_idea))
            db.session.commit()
    all_ideas = DateIdea.query.all()
    return render_template('date_ideas.html', ideas=all_ideas)


@app.route('/edit_idea/<int:idea_id>', methods=['POST'])
@login_required
@admin_required
def edit_idea(idea_id):
    idea = DateIdea.query.get_or_404(idea_id)
    edited_idea = request.form.get('edited_idea')
    if edited_idea:
        idea.idea = edited_idea
        db.session.commit()
    return redirect(url_for('date_ideas'))


@app.route('/delete_idea/<int:idea_id>', methods=['POST'])
@login_required
@admin_required
def delete_idea(idea_id):
    idea = DateIdea.query.get_or_404(idea_id)
    db.session.delete(idea)
    db.session.commit()
    return redirect(url_for('date_ideas'))


# ----------- GALLERY -----------
@app.route('/gallery', methods=['GET', 'POST'])
@login_required
def gallery():
    if request.method == 'POST' and session.get('role') == 'admin':
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(GALLERY_FOLDER, filename))
                db.session.add(GalleryImage(filename=filename))
                db.session.commit()
    images = GalleryImage.query.all()
    return render_template('gallery.html', images=images)


@app.route('/delete_image/<int:image_id>', methods=['POST'])
@login_required
@admin_required
def delete_image(image_id):
    image = GalleryImage.query.get_or_404(image_id)
    image_path = os.path.join(GALLERY_FOLDER, image.filename)
    if os.path.exists(image_path):
        os.remove(image_path)
    db.session.delete(image)
    db.session.commit()
    flash("Image deleted successfully.", "success")
    return redirect(url_for('gallery'))


# Notes page
@app.route("/notes", methods=["GET", "POST"])
@login_required
def notes():
    if "notes" not in app.config:
        app.config["notes"] = []

    if request.method == "POST" and session.get("role") == "admin":
        new_note = request.form.get("note")
        if new_note:
            app.config["notes"].append(new_note)
            flash("Note added!", "success")
        return redirect(url_for("notes"))

    return render_template("notes.html", notes=app.config["notes"])

@app.route("/delete_note/<int:idx>", methods=["POST"])
@login_required
def delete_note(idx):
    if session.get("role") == "admin" and "notes" in app.config:
        try:
            app.config["notes"].pop(idx)
            flash("Note deleted!", "info")
        except IndexError:
            flash("Note not found.", "danger")
    return redirect(url_for("notes"))



if __name__ == '__main__':
    app.run(debug=True)
