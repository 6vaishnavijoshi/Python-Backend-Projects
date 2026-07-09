import os
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
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

db = SQLAlchemy(app)

# -------------------------------
# Create Upload Folder
# -------------------------------

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

    title = db.Column(db.String(100), nullable=False)

    company = db.Column(db.String(100), nullable=False)

    location = db.Column(db.String(100), nullable=False)

    salary = db.Column(db.String(50))

    description = db.Column(db.Text)


class Application(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer)

    job_id = db.Column(db.Integer)

# -------------------------------
# Database Creation
# -------------------------------

with app.app_context():
    db.create_all()

# -------------------------------
# Helper Function
# -------------------------------

def allowed_file(filename):

    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

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

            return "Email already registered."

        hashed_password = generate_password_hash(password)

        user = User(
            name=name,
            email=email,
            password=hashed_password
        )

        db.session.add(user)

        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")

# -------------------------------
# Login
# -------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]

        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            session["user_id"] = user.id

            session["user_name"] = user.name

            return redirect(url_for("dashboard"))

        else:

            return "Invalid Email or Password"

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

            filename = secure_filename(file.filename)

            file.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

            flash("Resume Uploaded Successfully!")

            return redirect(url_for("dashboard"))

        else:

            flash("Only PDF files are allowed.")

    return render_template("upload_resume.html")


# -------------------------------
# Add Job
# -------------------------------

@app.route("/add_job", methods=["GET", "POST"])
def add_job():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        title = request.form["title"]
        company = request.form["company"]
        location = request.form["location"]
        salary = request.form["salary"]
        description = request.form["description"]

        new_job = Job(
            title=title,
            company=company,
            location=location,
            salary=salary,
            description=description
        )

        db.session.add(new_job)
        db.session.commit()

        flash("Job Added Successfully!")

        return redirect(url_for("jobs"))

    return render_template("add_job.html")

# -------------------------------
# View Jobs
# -------------------------------

@app.route("/jobs")
def jobs():

    if "user_id" not in session:
        return redirect(url_for("login"))

    jobs = Job.query.all()

    return render_template(
        "jobs.html",
        jobs=jobs
    )


# -------------------------------
# Apply Job
# -------------------------------

@app.route("/apply/<int:job_id>")
def apply(job_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    application = Application(
        user_id=session["user_id"],
        job_id=job_id
    )

    db.session.add(application)
    db.session.commit()

    flash("Application Submitted Successfully!")

    return redirect(url_for("jobs"))
# -------------------------------
# Logout
# -------------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))

# -------------------------------
# Run Application
# -------------------------------

if __name__ == "__main__":

    app.run(debug=True)