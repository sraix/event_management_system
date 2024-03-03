from flask import Flask, redirect, render_template, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask.helpers import url_for
from flask_login import UserMixin, login_required, logout_user, login_user, LoginManager, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, text
from datetime import datetime
from flask import json,jsonify

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
def load_user(id):
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
    end = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('event_categories.id'), nullable=False)
    moredetails = db.Column(db.Text)
    
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
from flask import request, jsonify, render_template
from datetime import datetime

@app.route('/admin/concerts/add', methods=['POST'])
@login_required
def add_event():
    
    if request.is_json:
        try:
            data = request.get_json()
            event = Event(
                name=data.get('name'),
                venue=data.get('venue'),
                date=datetime.strptime(data.get('start'), '%Y-%m-%dT%H:%M'),
                end=datetime.strptime(data.get('end'), '%Y-%m-%dT%H:%M'),
                description=data.get('description'),
                category_id=1,  # Assuming 'Concerts' category has id=1
                moredetails=data.get('moredetails')
            )
            db.session.add(event)
            db.session.commit()

            # Add tickets for the event
            for ticket_data in data.get('tickets', []):
                ticket = Ticket(
                    event_id=event.id,
                    ticket_type=ticket_data.get('ticket_type'),
                    price=ticket_data.get('price'),
                    available_tickets=ticket_data.get('available_tickets')
                )
                db.session.add(ticket)

            db.session.commit()
            return jsonify(success=True)
        except Exception as e:
            print(e)  # print the exception to the console, or log it if you have a logger set up
            db.session.rollback()  # rollback the transaction in case of error
            return jsonify(success=False, error=str(e)), 500
    return jsonify(success=False)


@app.route('/admin/concerts/delete/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get(event_id)
    if event:
        db.session.delete(event)
        db.session.commit()
        return jsonify(success=True)
    return jsonify(success=False)

@app.route('/admin/concerts/modify/<int:event_id>', methods=['GET'])
@login_required
def get_event_for_modify(event_id):
    event = Event.query.get(event_id)
    if event:
        # Convert event details to a dictionary
        event_details = {
            'name': event.name,
            'venue': event.venue,
            'date': event.date.strftime('%Y-%m-%dT%H:%M') if event.date else None,
            'end': event.end.strftime('%Y-%m-%dT%H:%M') if event.end else None,
            'description': event.description,
            'moredetails': event.moredetails,
            'tickets': []
        }

        # Include ticket details if available
        for ticket in event.tickets:
            event_details['tickets'].append({
                'id': ticket.id,
                'ticket_type': ticket.ticket_type,
                'price': ticket.price,
                'available_tickets': ticket.available_tickets
            })

        return jsonify(success=True, event=event_details)
    else:
        return jsonify(success=False, error='Event not found'), 404


@app.route('/admin/concerts/modify/<int:event_id>', methods=['POST'])
@login_required
def modify_event(event_id):
    event = Event.query.get(event_id)
    if event and request.is_json:
        data = request.get_json()
        print("Data received from client:", data)
        print("Keep ticket ids:", data.get('keep_ticket_ids', []))
        event.name = data.get('name', event.name)
        event.venue = data.get('venue', event.venue)
        event.date = datetime.strptime(data.get('date'), '%Y-%m-%dT%H:%M') if data.get('date') else event.date
        event.end = datetime.strptime(data.get('end'), '%Y-%m-%dT%H:%M') if data.get('end') else event.end
        event.description = data.get('description', event.description)
        event.moredetails = data.get('moredetails', event.moredetails)

        # Update tickets for the event
        for ticket_data in data.get('tickets', []):
            ticket = Ticket.query.get(ticket_data.get('id')) if 'id' in ticket_data else None
            if ticket:
                # Update existing ticket
                ticket.ticket_type = ticket_data.get('ticket_type', ticket.ticket_type)
                ticket.price = ticket_data.get('price', ticket.price)
                ticket.available_tickets = ticket_data.get('available_tickets', ticket.available_tickets)
            else:
                # Create new ticket
                ticket = Ticket(event_id=event.id, ticket_type=ticket_data.get('ticket_type'),
                                price=ticket_data.get('price'), available_tickets=ticket_data.get('available_tickets'))
                db.session.add(ticket)

        # Delete any tickets that weren't in the data
        if 'keep_ticket_ids' in data:
            for ticket in event.tickets:
                if ticket.id not in data.get('keep_ticket_ids', []):
                    db.session.delete(ticket)

        db.session.commit()
        return jsonify(success=True)
    return jsonify(success=False)


@app.route('/admin/concerts')
@login_required
def concerts1():
    # Assuming 'Concerts' category has id=1
    events = Event.query.filter_by(category_id=1).all()

    # Get the tickets for each event
    tickets = {event.id: Ticket.query.filter_by(event_id=event.id).all() for event in events}

    return render_template('adminconcert.html', events=events, tickets=tickets)



@app.route('/admin/festivals')
@login_required
def festivals1():
    # Assuming 'Concerts' category has id=1
    event2 = Event.query.filter_by(category_id=2).all()
    return render_template('adminfestival.html', events=event2)

@app.route('/admin/others')
@login_required
def others1():
    # Assuming 'Concerts' category has id=1
    event3 = Event.query.filter_by(category_id=3).all()
    return render_template('adminothers.html', events=event3)





@app.route('/book_ticket/<int:event_id>', methods=['POST'])
@login_required
def book_ticket(event_id):
    # Get the event and the number of tickets from the form data
    event = Event.query.get(event_id)
    ticket_id = request.form.get('ticket_type')
    ticket = Ticket.query.get(ticket_id)
    number_of_tickets = request.form.get('number_of_tickets')

    # Check if the event, ticket, and number_of_tickets are not None
    if event is None or ticket is None or number_of_tickets is None:
        return "Invalid request. Please try again."

    number_of_tickets = int(number_of_tickets)

    # Check if there are enough tickets available
    if ticket.available_tickets >= number_of_tickets:
        # Calculate the total price
        total_price = ticket.price * number_of_tickets

        # Create a new booking
        booking = Booking(user_id=current_user.id, event_id=event.id, ticket_id=ticket.id, date=datetime.now(), number_of_tickets=number_of_tickets, total_price=total_price)

        # Add the new booking to the database
        db.session.add(booking)

        # Update the number of available tickets
        ticket.available_tickets -= number_of_tickets

        # Commit the changes to the database
        db.session.commit()

        # Redirect the user to the events page
        return redirect(url_for('user'))

    else:
        flash('Not enough tickets available.', 'error')
        return redirect(url_for('concerts'))




from sqlalchemy import func

@app.route('/user/concerts')
@login_required
def concerts():
    # Assuming 'Concerts' category has id=1
    concerts = Event.query.filter_by(category_id=1).all()

    # Calculate the total number of available tickets for each event
    total_available_tickets = {}
    for concert in concerts:
        total_available_tickets[concert.id] = db.session.query(func.sum(Ticket.available_tickets)).filter(Ticket.event_id == concert.id).scalar()

    tickets = Ticket.query.filter(Ticket.event_id.in_([event.id for event in concerts])).all()
    tickets_json = json.dumps([{'id': ticket.id, 'price': str(ticket.price), 'available_tickets': ticket.available_tickets} for ticket in tickets])

    # Pass the total_available_tickets dictionary to the template
    return render_template('book.html', events=concerts, tickets=tickets, tickets_json=tickets_json, total_available_tickets=total_available_tickets)

@app.route('/user/festivals')
@login_required
def festivals():
    # Assuming 'Concerts' category has id=1
    festivals = Event.query.filter_by(category_id=2).all()

    # Calculate the total number of available tickets for each event
    total_available_tickets = {}
    for festival in festivals:
        total_available_tickets[festival.id] = db.session.query(func.sum(Ticket.available_tickets)).filter(Ticket.event_id == festival.id).scalar()

    tickets = Ticket.query.filter(Ticket.event_id.in_([event.id for event in festivals])).all()
    tickets_json = json.dumps([{'id': ticket.id, 'price': str(ticket.price), 'available_tickets': ticket.available_tickets} for ticket in tickets])

    # Pass the total_available_tickets dictionary to the template
    return render_template('book.html', events=festivals, tickets=tickets, tickets_json=tickets_json, total_available_tickets=total_available_tickets)

@app.route('/user/others')
@login_required
def others():
    # Assuming 'Concerts' category has id=1
    others = Event.query.filter_by(category_id=3).all()

    # Calculate the total number of available tickets for each event
    total_available_tickets = {}
    for other in others:
        total_available_tickets[other.id] = db.session.query(func.sum(Ticket.available_tickets)).filter(Ticket.event_id == other.id).scalar()

    tickets = Ticket.query.filter(Ticket.event_id.in_([event.id for event in others])).all()
    tickets_json = json.dumps([{'id': ticket.id, 'price': str(ticket.price), 'available_tickets': ticket.available_tickets} for ticket in tickets])

    # Pass the total_available_tickets dictionary to the template
    return render_template('book.html', events=others, tickets=tickets, tickets_json=tickets_json, total_available_tickets=total_available_tickets)

@app.route('/user/booking')
@login_required
def user_booking():
    # Assuming User and Booking are SQLAlchemy models and 'current_user' is the logged in user
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template('user_booking.html', bookings=bookings)



@app.route('/cancel_booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    # Get the booking from the database
    booking = Booking.query.get(booking_id)

    # Check if the booking exists and belongs to the current user
    if booking is None or booking.user_id != current_user.id:
        return "Booking not found", 404

    # Delete the booking
    db.session.delete(booking)
    db.session.commit()

    # Redirect the user to the bookings page
    return redirect(url_for('user'))



@app.route('/get_bookings', methods=['GET'])
@login_required
def get_bookings():
    # Get the bookings from the database
    bookings = Booking.query.filter_by(user_id=current_user.id).all()

    # Convert the bookings to a list of dictionaries
    bookings_list = [{'id': booking.id, 'event': booking.event.name, 'ticket_type': booking.ticket.ticket_type, 'number_of_tickets': booking.number_of_tickets} for booking in bookings]

    # Return the bookings as JSON
    return jsonify(bookings_list)



app.run(debug=True)
