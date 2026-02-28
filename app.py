from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import string
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///links.db'
db = SQLAlchemy(app)

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500))
    short_code = db.Column(db.String(10), unique=True)
    clicks = db.Column(db.Integer, default=0)

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/shorten', methods=['POST'])
def shorten():
    url = request.form['url']
    code = generate_code()
    new_link = Link(original_url=url, short_code=code)
    db.session.add(new_link)
    db.session.commit()
    return f"Short URL: http://127.0.0.1:5000/{code}"

@app.route('/<code>')
def redirect_to_url(code):
    link = Link.query.filter_by(short_code=code).first()
    if link:
        link.clicks += 1
        db.session.commit()
        return render_template("ad_page.html", url=link.original_url)
    return "Invalid URL"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)