from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import string
import random
import os

app = Flask(__name__)

# -------------------------
# DATABASE CONFIGURATION
# -------------------------

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Render PostgreSQL fix (if you add later)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
else:
    # Fallback to SQLite (for local)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///links.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "connect_args": {"check_same_thread": False}
}

db = SQLAlchemy(app)

# -------------------------
# DATABASE MODEL
# -------------------------

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)
    clicks = db.Column(db.Integer, default=0)

# -------------------------
# UTIL FUNCTION
# -------------------------

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# -------------------------
# ROUTES
# -------------------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/shorten", methods=["POST"])
def shorten():
    url = request.form.get("url")

    if not url:
        return "URL is required", 400

    # Ensure unique short code
    while True:
        code = generate_code()
        if not Link.query.filter_by(short_code=code).first():
            break

    new_link = Link(original_url=url, short_code=code)
    db.session.add(new_link)
    db.session.commit()

    short_url = request.host_url + code
    return f"Short URL: {short_url}"

@app.route("/<code>")
def redirect_to_url(code):
    link = Link.query.filter_by(short_code=code).first()

    if not link:
        return "Invalid URL", 404

    link.clicks += 1
    db.session.commit()

    return render_template("ad_page.html", url=link.original_url)

# -------------------------
# INIT DB
# -------------------------

with app.app_context():
    db.create_all()

# -------------------------
# LOCAL RUN
# -------------------------

if __name__ == "__main__":
    app.run()