from ai.parser import extract_text
from ai.skills import extract_skills
from ai.extract_email import extract_email
from ai.extract_phone import extract_phone

import os

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_from_directory
)

from flask_sqlalchemy import SQLAlchemy

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from werkzeug.utils import secure_filename

# -------------------------------
# Flask Configuration
# -------------------------------

app = Flask(__name__)

app.config["SECRET_KEY"] = "mysecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"pdf"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)

# -------------------------------
# Database Model
# -------------------------------

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Job(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100))

    company = db.Column(db.String(100))

    skills = db.Column(db.Text)

# -------------------------------
# Create Database
# -------------------------------

with app.app_context():
    db.create_all()

# -------------------------------
# Helper Function
# -------------------------------

def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

# -------------------------------
# Home
# -------------------------------

@app.route("/")
def home():
    return render_template("index.html")

# -------------------------------
# Register
# -------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already registered.")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        user = User(
            name=name,
            email=email,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        flash("Registration Successful!")

        return redirect(url_for("login"))

    return render_template("register.html")

# -------------------------------
# Login
# -------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            session["user_id"] = user.id
            session["user_name"] = user.name

            flash("Login Successful!")

            return redirect(url_for("dashboard"))

        flash("Invalid Email or Password")

    return render_template("login.html")

# -------------------------------
# Dashboard
# -------------------------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    files = os.listdir(app.config["UPLOAD_FOLDER"])

    return render_template(
        "dashboard.html",
        name=session["user_name"],
        files=files
    )
# -------------------------------
# Upload Resume
# -------------------------------

@app.route("/upload", methods=["GET", "POST"])
def upload():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        if "resume" not in request.files:
            flash("No file selected")
            return redirect(request.url)

        file = request.files["resume"]

        if file.filename == "":
            flash("No file selected")
            return redirect(request.url)

        if file and allowed_file(file.filename):

            # Secure filename
            filename = secure_filename(file.filename)

            # Save PDF
            filepath = os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )

            file.save(filepath)

            # -------------------------------
            # AI Resume Parsing
            # -------------------------------

            text = extract_text(filepath)

            email = extract_email(text)

            phone = extract_phone(text)

            skills = extract_skills(text)

            # -------------------------------
            # Day 7 - Resume Scoring
            # -------------------------------

            job_skills = [
                "Python",
                "Flask",
                "SQL",
                "HTML",
                "CSS",
                "JavaScript",
                "React"
            ]

            matched = []

            for skill in job_skills:
                if skill in skills:
                    matched.append(skill)

            percentage = int((len(matched) / len(job_skills)) * 100)

            score = min(100, percentage + 10)

            if score >= 70:
                status = "⭐ Shortlisted"
            else:
                status = "❌ Rejected"

            flash("Resume Uploaded Successfully!")

            return render_template(
                "resume_result.html",
                filename=filename,
                email=email,
                phone=phone,
                skills=skills,
                matched=matched,
                percentage=percentage,
                score=score,
                status=status,
                text=text
            )

        else:
            flash("Only PDF files are allowed.")

    return render_template("upload_resume.html")

    #--------------------------------
    #Download Route
    #-------------------------------
@app.route("/download/<filename>")
def download(filename):

    if "user_id" not in session:
        return redirect(url_for("login"))

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename,
        as_attachment=True
    )

# -------------------------------
# Logout
# -------------------------------

@app.route("/logout")
def logout():

    session.clear()

    flash("Logged Out Successfully!")

    return redirect(url_for("login"))


#--------------------------
#View Route
#---------------------------
@app.route("/view/<filename>")
def view_resume(filename):

    if "user_id" not in session:
        return redirect(url_for("login"))

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )

#-------------------------------
#Delete Route
#-------------------------------
@app.route("/delete_resume/<filename>")
def delete_resume(filename):

    if "user_id" not in session:
        return redirect(url_for("login"))

    path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    if os.path.exists(path):
        os.remove(path)

    flash("Resume Deleted")

    return redirect(url_for("dashboard"))


#--------------------------------
#job Match Route
#-------------------------------
@app.route("/job_match", methods=["GET", "POST"])
def job_match():

    if "resume_skills" not in session:
        flash("Please upload a resume first.")
        return redirect(url_for("upload"))

    if request.method == "POST":

        required_skills = request.form["skills"]

        required_skills = [
            skill.strip().lower()
            for skill in required_skills.split(",")
        ]

        resume_skills = [
            skill.lower()
            for skill in session["resume_skills"]
        ]

        matched = []

        missing = []

        for skill in required_skills:

            if skill in resume_skills:
                matched.append(skill)

            else:
                missing.append(skill)

        percentage = int(
            (len(matched) / len(required_skills)) * 100
        )

        return render_template(
            "match_result.html",
            matched=matched,
            missing=missing,
            percentage=percentage
        )

    return render_template("job_match.html")


#--------------------------------
#add_job Route
#---------------------------------
@app.route("/add_job", methods=["GET", "POST"])
def add_job():

    if request.method == "POST":

        job = Job(

            title=request.form["title"],

            company=request.form["company"],

            skills=request.form["skills"]

        )

        db.session.add(job)

        db.session.commit()

        flash("Job Added Successfully!")

        return redirect(url_for("jobs"))

    return render_template("add_job.html")

# -------------------------------
# Run Flask
# -------------------------------

if __name__ == "__main__":
    app.run(debug=True)