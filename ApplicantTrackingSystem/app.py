from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

# Create Flask application
app = Flask(__name__)

# Configure SQLite Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize Database
db = SQLAlchemy(app)

# -------------------------
# Database Model
# -------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<User {self.name}>"

# Create database and tables
with app.app_context():
    db.create_all()

# -------------------------
# Home Page
# -------------------------
@app.route("/")
def home():
    return render_template("index.html")

# -------------------------
# Register Page
# -------------------------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return "Email already registered!"

        # Create new user
        new_user = User(
            name=name,
            email=email,
            password=password
        )

        # Save user
        db.session.add(new_user)
        db.session.commit()

        return "Registration Successful!"

    return render_template("register.html")

# -------------------------
# Login Page
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(
            email=email,
            password=password
        ).first()

        if user:
            return f"Welcome {user.name}!"

        return "Invalid Email or Password"

    return render_template("login.html")

# -------------------------
# Run Application
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)