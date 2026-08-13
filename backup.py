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

app = Flask(__name__)

app.secret_key = "deepvision_secret_key"

# ---------------------------------------
# Configuration
# ---------------------------------------

DATABASE = "database/deepvision.db"

UPLOAD_FOLDER = "static/uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ---------------------------------------
# Database Connection
# ---------------------------------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------
# Home
# ---------------------------------------

@app.route("/")
def home():
    return redirect(url_for("login"))


# ---------------------------------------
# Login
# ---------------------------------------

@app.route("/login")
def login():
    return render_template("login.html")


# ---------------------------------------
# Signup
# ---------------------------------------

@app.route("/signup")
def signup():
    return render_template("signup.html")


# ---------------------------------------
# Dashboard
# ---------------------------------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html")


# ---------------------------------------
# Detect Page
# ---------------------------------------

@app.route("/detect")
def detect():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("detect.html")


# ---------------------------------------
# Result Page
# ---------------------------------------

@app.route("/result")
def result():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("result.html")


# ---------------------------------------
# Logout
# ---------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# ---------------------------------------

if __name__ == "__main__":
    app.run(debug=True)