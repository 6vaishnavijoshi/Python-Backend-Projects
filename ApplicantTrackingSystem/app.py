from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# -------------------------------
# Create Flask App
# -------------------------------
app = Flask(__name__)

# Secret Key for Sessions
app.secret_key = "ATS_Project_2026"

# SQLite Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize Database
db = SQLAlchemy(app)

# -------------------------------
# Database Model
# -------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(100), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<User {self.name}>"


# Create Database
with app.app_context():
    db.create_all()


# -------------------------------
# Home Page
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

        # Check duplicate email
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return "Email already exists!"

        # Hash Password
        hashed_password = generate_password_hash(password)

        # Create User
        new_user = User(
            name=name,
            email=email,
            password=hashed_password
        )

        # Save to Database
        db.session.add(new_user)
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

    return render_template(
        "dashboard.html",
        name=session["user_name"]
    )


# -------------------------------
# Logout
# -------------------------------
@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# -------------------------------
# Run App
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)