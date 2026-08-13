"""
====================================================
DeepVision AI
Flask Web Application
====================================================
"""

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

import os
import sqlite3
from werkzeug.utils import secure_filename

# Import AI Prediction Function
from predict import predict_image

# Import Database Initialization
from database import create_database
# ----------------------------------------------------
# Flask App
# ----------------------------------------------------

app = Flask(__name__)

app.secret_key = "deepvision_secret_key"

# ----------------------------------------------------
# Configuration
# ----------------------------------------------------

DATABASE = "database/deepvision.db"

UPLOAD_FOLDER = "static/uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}

# ----------------------------------------------------
# Database
# ----------------------------------------------------

def get_db():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


# ----------------------------------------------------
# Helper Functions
# ----------------------------------------------------

def allowed_file(filename):

    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# ----------------------------------------------------
# Home
# ----------------------------------------------------

@app.route("/")
def home():

    return render_template("index.html")


# ----------------------------------------------------
# Login
# ----------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM users
            WHERE email=? AND password=?
            """,
            (email, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            session["user_id"] = user["id"]
            session["username"] = user["username"]

            flash("Welcome back!", "success")

            return redirect(url_for("dashboard"))

        flash("Invalid email or password!", "danger")

    return render_template("login.html")


# ----------------------------------------------------
# Signup
# ----------------------------------------------------

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        existing = cursor.fetchone()

        if existing:

            conn.close()

            flash("Email already exists!", "warning")

            return redirect(url_for("signup"))

        cursor.execute(
            """
            INSERT INTO users(username,email,password)
            VALUES(?,?,?)
            """,
            (
                username,
                email,
                password
            )
        )

        conn.commit()

        conn.close()

        flash("Account created successfully!", "success")

        return redirect(url_for("login"))

    return render_template("signup.html")

# ----------------------------------------------------
# Logout
# ----------------------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully.", "info")

    return redirect(url_for("login"))


# ----------------------------------------------------
# Dashboard
# ----------------------------------------------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*) as total
        FROM predictions
        WHERE user_id=?
        """,
        (session["user_id"],)
    )

    total_predictions = cursor.fetchone()["total"]

    conn.close()

    return render_template(
        "dashboard.html",
        total_predictions=total_predictions
    )


# ----------------------------------------------------
# Detect Page
# ----------------------------------------------------

@app.route("/detect")
def detect():

    if "user_id" not in session:

        return redirect(url_for("login"))

    return render_template("detect.html")


# ----------------------------------------------------
# Predict
# ----------------------------------------------------

@app.route("/predict", methods=["POST"])
def predict():

    if "user_id" not in session:

        return redirect(url_for("login"))

    if "image" not in request.files:

        flash("No image selected.")

        return redirect(url_for("detect"))

    file = request.files["image"]

    if file.filename == "":

        flash("Please select an image.")

        return redirect(url_for("detect"))

    if not allowed_file(file.filename):

        flash("Only JPG, JPEG, PNG and WEBPimages are allowed.")

        return redirect(url_for("detect"))

    filename = secure_filename(file.filename)

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )
    file.save(filepath)

    print("=" * 60)
    print("Uploaded file path:", filepath)

    result = predict_image(filepath)

    print("Prediction Result:", result)
    print("=" * 60)

    prediction = result["label"]

    confidence = result["confidence"]

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO predictions
        (
            user_id,
            image_name,
            prediction,
            confidence
        )
        VALUES(?,?,?,?)
        """,
        (
            session["user_id"],
            filename,
            prediction,
            confidence
        )
    )

    conn.commit()

    conn.close()

    return render_template(

        "result.html",

        prediction=prediction,

        confidence=confidence,

        image_path="/" + filepath.replace("\\", "/")
    )


# ----------------------------------------------------
# Result
# ----------------------------------------------------

@app.route("/result")
def result():

    if "user_id" not in session:

        return redirect(url_for("login"))

    return render_template("result.html")

# ----------------------------------------------------
# History
# ----------------------------------------------------

@app.route("/history")
def history():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM predictions
        WHERE user_id=?
        ORDER BY created_at DESC
        """,
        (session["user_id"],)
    )

    predictions = cursor.fetchall()

    conn.close()

    return render_template(
        "history.html",
        predictions=predictions
    )

if __name__ == "__main__":

    create_database()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )