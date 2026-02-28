from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import string
import random
import os

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    "DATABASE_URL",
    "sqlite:///links.db"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Model
class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)
    clicks = db.Column(db.Integer, default=0)


# Generate random short code
def generate_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


# Home Page
@app.route('/')
def index():
    return render_template("index.html")


# Shorten URL
@app.route('/shorten', methods=['POST'])
def shorten():
    url = request.form['url']

    # Generate unique code
    while True:
        code = generate_code()
        if not Link.query.filter_by(short_code=code).first():
            break

    new_link = Link(original_url=url, short_code=code)
    db.session.add(new_link)
    db.session.commit()

    short_url = request.host_url + code
    return f"Short URL: {short_url}"


# Redirect with Ad Page
@app.route('/<code>')
def redirect_to_url(code):
    link = Link.query.filter_by(short_code=code).first()

    if link:
        link.clicks += 1
        db.session.commit()
        return render_template("ad_page.html", url=link.original_url)

    return "Invalid URL", 404


# Create database tables
with app.app_context():
    db.create_all()


# Run only if local
if __name__ == "__main__":
    app.run()