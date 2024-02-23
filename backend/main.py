from flask import Flask, redirect, render_template, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask.helpers import url_for
from flask_login import UserMixin, login_required, logout_user, login_user, LoginManager, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, text
from datetime import datetime
from flask import json

# mydatabase connection
local_server = True
app = Flask(__name__)
app.secret_key = "sraix"

# this is for getting unique user access
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "userlogin"

#app.config
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/testing'
db = SQLAlchemy(app)

#admin details
with open('config.json','r') as c:
    params=json.load(c)["params"]

@login_manager.user_loader
def load_user(userid):
    return users.query.get(int(userid))

@login_manager.user_loader
def load_user(username):
    return params.get(username)

# users  table in the database
class users(UserMixin, db.Model):
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    email = db.Column(db.String(20))
    password = db.Column(db.String(1000))
    def get_id(self):
        return str(self.userid)
    
class User(UserMixin):
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def get_id(self):
        return self.username

@app.route("/")
def home():
    return render_template("homepage.html")

@app.route("/usersignup")
def usersignup():
    return render_template("usersignup.html")

#user signup
@app.route('/signup', methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get('email')
        password = request.form.get("password")
        encapassword = generate_password_hash(password)
        
        # Check if the user already exists before adding them to the database
        user = users.query.filter_by(email=email).first()
        user1 = users.query.filter_by(username=username).first()
        if user or user1:
            flash("Username or Email already exists","warning")
            return render_template("usersignup.html")
        
        # If the user doesn't exist, add them to the database
        new_user = users(username=username, email=email, password=encapassword)
        db.session.add(new_user)  # Add the new user to the session
        db.session.commit()  # Commit (save) the changes

        flash("Sign Up Success, Please Login", "success")
        return render_template("userlogin.html")
        
    return render_template("usersignup.html")

#clear cache
@app.after_request
def add_no_cache(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.before_request
def before_request():
    if 'logged_in' in session:
        if session.get('user_type') == 'user':
            user_record = users.query.filter_by(email=session['email']).first()
            if user_record:
                login_user(user_record)
        elif session.get('user_type') == 'admin':
            if params['email'] == session['email']:
                # Create an admin object with the details from params
                admin_record = User(params['username'], params['email'], params['password'])
                login_user(admin_record)
#user login
@app.route('/userlogin', methods=["POST", "GET"])
def userlogin():
    error=None
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get("password")
        user_record = users.query.filter_by(email=email).first()
        if user_record and check_password_hash(user_record.password, password):
            login_user(user_record)
            session['logged_in'] = True
            session['email'] = email
            session['username'] = user_record.username
            session['user_type'] = 'user'  # Set user type
            return redirect(url_for("user"))
        else:
            flash("Invalid Credentials", "danger")
            error = 'Invalid Credentials. Please try again.'
    return render_template('userlogin.html', error=error)

@app.route('/user')
def user():
    if not session.get('logged_in'):
        return redirect(url_for('userlogin'))
    else:
        return render_template("user.html")

#admin login
@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get("password")
        
        if(email==params['email'] and password==params['password']):
            # Create an admin object with the details from params
            admin_record = User(params['username'], params['email'], params['password'])
            login_user(admin_record)
            session['logged_in'] = True
            session['email'] = email
            session['username'] = params['username']
            session['user_type'] = 'admin'   #Set user type to admin
            return redirect(url_for("index"))
        else:
            flash("Invalid Credentials", "danger")
            error = 'Invalid Credentials. Please try again.'
    return render_template('adminlogin.html', error=error)

@app.route('/index')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('adminlogin'))
    else:
        return render_template('index.html')

@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect("/")




#just testing


#database intiating
class event_categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

class events(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    venue = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.String(1000))
    ticketprice = db.Column(db.String(11))
    category_id = db.Column(db.Integer, db.ForeignKey('event_categories.id'), nullable=False)
    available_tickets = db.Column(db.Integer, nullable=False)

    category = db.relationship('event_categories', backref=db.backref('events', lazy=True))

class bookings(db.Model):
    booking_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.userid'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    booking_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    number_of_tickets = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

    user = db.relationship('users', backref=db.backref('bookings', lazy=True))
    event = db.relationship('events', backref=db.backref('bookings', lazy=True))


@app.route('/book_ticket/<int:event_id>', methods=['POST'])
@login_required
def book_ticket(event_id):
    # Get the event and the number of tickets from the form data
    event = events.query.get(event_id)
    number_of_tickets = int(request.form.get('number_of_tickets'))

    # Check if there are enough tickets available
    if event.available_tickets >= number_of_tickets:
        # Calculate the total price
        total_price = event.ticketprice * number_of_tickets

        # Create a new booking
        booking = bookings(user_id=current_user.userid, event_id=event_id, booking_date=datetime.now(), number_of_tickets=number_of_tickets, total_price=total_price)

        # Add the new booking to the database
        db.session.add(booking)

        # Update the number of available tickets
        event.available_tickets -= number_of_tickets

        # Commit the changes to the database
        db.session.commit()

        # Redirect the user to the events page
        return redirect(url_for('user'))
    else:
        # If there are not enough tickets available, show an error message
        return "Sorry, there are not enough tickets available for this event."


@app.route('/user/concerts')
@login_required
def concerts():
    # Assuming 'Concerts' category has id=1
    concerts = events.query.filter_by(category_id=1).all()
    return render_template('book.html', events=concerts)


@app.route('/user/festivals')
@login_required
def festivals():
    # Assuming 'Concerts' category has id=1
    festivals = events.query.filter_by(category_id=2).all()
    return render_template('book.html', events=festivals)

@app.route('/user/others')
@login_required
def others():
    # Assuming 'Concerts' category has id=1
    others = events.query.filter_by(category_id=3).all()
    return render_template('book.html', events=others)



app.run(debug=True)
