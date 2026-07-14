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
# Login Page
# -------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        print("Email:", email)

        user = User.query.filter_by(email=email).first()

        if user:
            print("User Found")
        else:
            print("User Not Found")

        if user and check_password_hash(user.password, password):

            print("Password Correct")

            session["user_id"] = user.id
            session["user_name"] = user.name

            return redirect(url_for("dashboard"))

        else:

            print("Wrong Password")

            flash("Invalid Email or Password")

    return render_template("login.html")


       #----------------------------------
@app.route("/logout")
def logout():

    session.clear()

    flash("Logged Out Successfully!")

    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        name=session["user_name"]
    )
# -------------------------------
# Run Flask App
# -------------------------------

if __name__ == "__main__":
    app.run(debug=True)