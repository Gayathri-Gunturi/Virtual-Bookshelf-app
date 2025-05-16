from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField
from wtforms.validators import DataRequired
from flask_login import LoginManager, UserMixin, login_user, current_user
from flask_login import logout_user
import os


app = Flask(__name__)
app.secret_key = 'abcde'

# Configure SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///collections.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# User model
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    books = db.relationship('Book', back_populates='user')

# Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    review = db.Column(db.String(500), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('Users', back_populates='books')

# WTForms Form
class LoginForm(FlaskForm):
    id = IntegerField('Id', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    rating = FloatField('Rating', validators=[DataRequired()])
    review = StringField('Review', validators=[DataRequired()])

# Flask-Login user loader
@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)

# Routes
@app.route('/')
def homes():
    return render_template('login.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        
        # Check if the username already exists
        existing_user = Users.query.filter_by(username=username).first()
        if existing_user:
            return render_template("signup.html", error="Username already exists.")
        
        # Check if the email already exists
        existing_email = Users.query.filter_by(email=email).first()
        if existing_email:
            return render_template("signup.html", error="Email already registered.")
        
        user = Users(username=username, password=password, email=email)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = Users.query.filter_by(username=request.form.get("username")).first()
        if user and user.password == request.form.get("password"):
            login_user(user)
            return redirect(url_for("returns"))
        else:
            return render_template("login.html", error="Invalid username or password.")
    return render_template("login.html")

@app.route('/index')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    books = Book.query.filter_by(user_id=current_user.id).all()
    return render_template("index.html", books=books)

@app.route("/add", methods=['GET', 'POST'])
def add():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        new_book = Book(
            title=login_form.title.data,
            author=login_form.author.data,
            rating=login_form.rating.data,
            review=login_form.review.data,
            user_id=current_user.id
        )
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template("add.html", form=login_form)

@app.route('/returns')
def returns():
    return render_template('homepage.html')

@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('login'))


if not os.path.exists('collections.db'):
    with app.app_context():
        db.create_all()

# Initialize database
# with app.app_context():
#     db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
