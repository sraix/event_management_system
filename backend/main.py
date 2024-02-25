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
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/event_management_system'
db = SQLAlchemy(app)

#admin details
with open('config.json','r') as c:
    params=json.load(c)["params"]

@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(id))

@login_manager.user_loader
def load_user(username):
    return params.get(username)

#initializing json file  
class Admin(UserMixin):
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def get_id(self):
        return self.username

#initializing users table in database   
class User(UserMixin,db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(1000), nullable=False)
    registeredon=db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship('Booking', backref='user', lazy=True, cascade="all, delete-orphan")
    reviews = db.relationship('Review', backref='user', lazy=True, cascade="all, delete-orphan")
    def get_id(self):
         return str(self.id)


#initializing event_categories table in database     
class EventCategory(db.Model):
    __tablename__ = 'event_categories'

    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    events = db.relationship('Event', backref='category', lazy=True)

#initializing events table in database
class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    venue = db.Column(db.String(100))
    date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('event_categories.id'), nullable=False)
    moredetails = db.Column(db.Text)
    facilities = db.Column(db.Text)

    bookings = db.relationship('Booking', backref='event', lazy=True)
    reviews = db.relationship('Review', backref='event', lazy=True)
    tickets = db.relationship('Ticket', backref='event', lazy=True)

#initializing bookings table in database
class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    number_of_tickets = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)

#initializing tickets table in database
class Ticket(db.Model):
    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    ticket_type = db.Column(db.String(50))
    price = db.Column(db.Numeric(10, 2))
    available_tickets = db.Column(db.Integer)

    bookings = db.relationship('Booking', backref='ticket', lazy=True)

#initializing reviews table in database
class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    rating = db.Column(db.Integer)
    review_text = db.Column(db.Text)
    review_date = db.Column(db.Date)

#landing page
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
        user = User.query.filter_by(email=email).first()
        user1 = User.query.filter_by(name=username).first()
        if user or user1:
            flash("Username or Email already exists","warning")
            return render_template("usersignup.html")
        
        # If the user doesn't exist, add them to the database
        new_user = User(name=username, email=email, password=encapassword)
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
            user_record = User.query.filter_by(email=session['email']).first()
            if user_record:
                login_user(user_record)
        elif session.get('user_type') == 'admin':
            if params['email'] == session['email']:
                # Create an admin object with the details from params
                admin_record = Admin(params['username'], params['email'], params['password'])
                login_user(admin_record)
#user login
@app.route('/userlogin', methods=["POST", "GET"])
def userlogin():
    error=None
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get("password")
        user_record = User.query.filter_by(email=email).first()
        if user_record and check_password_hash(user_record.password, password):
            login_user(user_record)
            session['logged_in'] = True
            session['email'] = email
            session['username'] = user_record.name
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
            admin_record = Admin(params['username'], params['email'], params['password'])
            login_user(admin_record)
            session['logged_in'] = True
            session['email'] = email
            session['username'] = params['username']
            session['user_type'] = 'admin'   #Set user type to admin
            return redirect(url_for("admin"))
        else:
            flash("Invalid Credentials", "danger")
            error = 'Invalid Credentials. Please try again.'
    return render_template('adminlogin.html', error=error)

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('adminlogin'))
    else:
        return render_template('admin.html')
    


@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect("/")




#just testing
@app.route('/admin/concerts')
@login_required
def concerts1():
    # Assuming 'Concerts' category has id=1
    event1 = Event.query.filter_by(category_id=1).all()
    return render_template('adminconcert.html', events=event1)

@app.route('/admin/festivals')
@login_required
def festivals1():
    # Assuming 'Concerts' category has id=1
    event2 = Event.query.filter_by(category_id=1).all()
    return render_template('adminfestival.html', events=event2)

@app.route('/admin/others')
@login_required
def others1():
    # Assuming 'Concerts' category has id=1
    event3 = Event.query.filter_by(category_id=1).all()
    return render_template('adminothers.html', events=event3)




@app.route('/book_ticket/<int:event_id>', methods=['POST'])
@login_required
def book_ticket(event_id):
    # Get the event and the number of tickets from the form data
    event = Event.query.get(event_id)
    number_of_tickets = int(request.form.get('number_of_tickets'))

    # Check if there are enough tickets available
    if event.available_tickets >= number_of_tickets:
        # Calculate the total price
        total_price = event.ticketprice * number_of_tickets

        # Create a new booking
        booking = Booking(user_id=current_user.userid, event_id=event_id, booking_date=datetime.now(), number_of_tickets=number_of_tickets, total_price=total_price)

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
    concerts = Event.query.filter_by(category_id=1).all()
    return render_template('book.html', events=concerts)


@app.route('/user/festivals')
@login_required
def festivals():
    # Assuming 'Concerts' category has id=1
    festivals = Event.query.filter_by(category_id=2).all()
    return render_template('book.html', events=festivals)

@app.route('/user/others')
@login_required
def others():
    # Assuming 'Concerts' category has id=1
    others = Event.query.filter_by(category_id=3).all()
    return render_template('book.html', events=others)



app.run(debug=True)
