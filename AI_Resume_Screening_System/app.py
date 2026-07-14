from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# -------------------------------
# Flask Configuration
# -------------------------------

app = Flask(__name__)

app.config["SECRET_KEY"] = "mysecretkey"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# -------------------------------
# Database Model
# -------------------------------

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(100), unique=True, nullable=False)

    password = db.Column(db.String(200), nullable=False)

# -------------------------------
# Create Database
# -------------------------------

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

        user = User(
            name=name,
            email=email,
            password=password
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")

# -------------------------------
# Login Page
# -------------------------------

@app.route("/login")
def login():
    return render_template("login.html")

# -------------------------------
# Run Flask App
# -------------------------------

if __name__ == "__main__":
    app.run(debug=True)