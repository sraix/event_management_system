from flask import Flask, redirect, render_template, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask.helpers import url_for
from flask_login import UserMixin, login_required, logout_user, login_user, LoginManager, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, text
from datetime import datetime
from flask import json,jsonify

from sqlalchemy import func
from flask import request, jsonify, render_template
from datetime import datetime
import mysql.connector


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
    tickets = db.relationship('Ticket', backref='event', lazy=True, cascade="all,delete")
    

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

    reviews = db.relationship('Review', backref='booking', lazy=True, cascade="all, delete-orphan") 

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
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    rating = db.Column(db.Integer)
    review_text = db.Column(db.Text)
    review_date = db.Column(db.Date)



#landing page
@app.route("/")
def home():
    return render_template("homepage.html")


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


##USER SECTION BELOW>>>>......>>>>>

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
    
from sqlalchemy import text

@app.route('/book_ticket/<int:event_id>', methods=['POST'])
@login_required
def book_ticket(event_id):
    # Get the event and the number of tickets from the form data
    event = Event.query.get(event_id)

    if event is None or event.end < datetime.now():
        flash('This event has ended. You cannot book tickets for it.', 'error')
        return redirect(request.referrer)
    
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
        flash('Booking Success!!', 'success')
        return redirect(request.referrer)

    else:
        flash('Not enough tickets available.', 'error')
        return redirect(request.referrer)





@app.route('/cancel_booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    # Create a new MySQL connection
    cnx = mysql.connector.connect(user='root', password='', host='localhost', database='event_management_system')

    # Create a new cursor
    cursor = cnx.cursor()

    # Call the stored procedure
    cursor.callproc('CancelBooking', args=(booking_id, current_user.id))

    # Commit the changes and close the connection
    cnx.commit()
    cnx.close()

    # Redirect the user to the bookings page
    return redirect(url_for('user_booking'))





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
    return render_template('book.html', events=concerts, tickets=tickets, tickets_json=tickets_json, total_available_tickets=total_available_tickets,current_time=datetime.now())

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
    return render_template('book.html', events=festivals, tickets=tickets, tickets_json=tickets_json, total_available_tickets=total_available_tickets,current_time=datetime.now())

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
    return render_template('book.html', events=others, tickets=tickets, tickets_json=tickets_json, total_available_tickets=total_available_tickets,current_time=datetime.now())


@app.route('/user/booking')
@login_required
def user_booking():
    # Assuming User and Booking are SQLAlchemy models and 'current_user' is the logged in user
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    current_time = datetime.utcnow()
    return render_template('user_booking.html', bookings=bookings, current_time=current_time)


@app.route('/submit_review/<int:event_id>', methods=['POST'])
@login_required
def submit_review(event_id):
    review_text = request.form.get('review_text')
    rating = request.form.get('rating')
    print(review_text)
    print(rating)
    # Check if the user has already reviewed this event
    existing_review = Review.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if existing_review:
        flash('You have already reviewed this event.', 'error')
        return redirect(url_for('user_booking'))
    
    # Get the booking made by the current user for the given event
    booking = Booking.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if not booking:
        flash('No booking found for this event.', 'error')
        return redirect(url_for('user_booking'))

    # Create a new review
    review = Review(user_id=current_user.id, event_id=event_id, booking_id=booking.id, review_text=review_text, rating=rating, review_date=datetime.utcnow())
    db.session.add(review)
    db.session.commit()
    flash('Your review has been submitted.', 'success')
    return redirect(url_for('user_booking'))

@app.route('/user/reviews')
@login_required
def reviews():
    # Assuming Review is a SQLAlchemy model
    
    reviews = Review.query.filter_by(user_id=current_user.id).all()
    # Pass a variable indicating whether there are reviews or not
    has_reviews = bool(reviews)

    if not has_reviews:
        flash('You have no Reviews!!', 'warning')

    return render_template('reviews.html', reviews=reviews, has_reviews=has_reviews)



@app.route('/delete_review/<int:review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    # Assuming Review is a SQLAlchemy model
    review = Review.query.get(review_id)
    if review and review.user_id == current_user.id:
        db.session.delete(review)
        db.session.commit()
        flash('Your review has been deleted.', 'success')
        return redirect(url_for('user'))
    else:
        flash('Review not found.', 'error')
    return redirect(url_for('reviews'))





##ADMIN SECTION BELOW >>>>>>........>>>>>>>

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
        # Fetch recent bookings data
        recent_bookings = Booking.query.order_by(Booking.date.desc()).limit(5).all()

        # Fetch total number of tickets booked
        total_tickets_booked = Booking.query.with_entities(func.sum(Booking.number_of_tickets)).scalar()
        total_tickets_booked = total_tickets_booked if total_tickets_booked else 0

        # Fetch total revenue earned
        total_revenue_earned = Booking.query.with_entities(func.sum(Booking.total_price)).scalar()
        total_revenue_earned = total_revenue_earned if total_revenue_earned else 0

        # Fetch count of registered users
        total_registered_users = User.query.count()

        # Prepare the data for the template
        data = []
        for booking in recent_bookings:
            ticket_type = booking.ticket.ticket_type if booking.ticket else 'N/A'

            data.append({
                'user_name': booking.user.name if booking.user else 'N/A',
                'event_type': booking.event.category.category_name if booking.event and booking.event.category else 'N/A',
                'event_name': booking.event.name if booking.event else 'N/A',
                'ticket_type': ticket_type,
                'booking_date': booking.date,
                'number_of_tickets': booking.number_of_tickets
            })

        return render_template(
            'admin.html',
            data=data,
            total_tickets_booked=total_tickets_booked,
            total_revenue_earned=total_revenue_earned,
            total_registered_users=total_registered_users
        )


#logout
@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect("/")



@app.route('/admin/concerts')
@login_required
def concerts1():
    # Assuming 'Concerts' category has id=1
    events = Event.query.filter_by(category_id=1).all()
    

    # Get the tickets for each event
    tickets = {event.id: Ticket.query.filter_by(event_id=event.id).all() for event in events}
    if not events:
        flash('No concerts are available, Consider adding one...!', 'info')

    return render_template('adminconcert.html', events=events, tickets=tickets)

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

        # Keep track of existing ticket ids to delete if not present in the new data
        existing_ticket_ids = [ticket.id for ticket in event.tickets]

        # Update existing tickets and create new ones
        for ticket_data in data.get('tickets', []):
            ticket_id = ticket_data.get('id')
            if ticket_id in existing_ticket_ids:
                # Update existing ticket
                ticket = Ticket.query.get(ticket_id)
                ticket.ticket_type = ticket_data.get('ticket_type', ticket.ticket_type)
                ticket.price = ticket_data.get('price', ticket.price)
                ticket.available_tickets = ticket_data.get('available_tickets', ticket.available_tickets)
                existing_ticket_ids.remove(ticket_id)
            else:
                # Create new ticket
                ticket = Ticket(
                    event_id=event.id,
                    ticket_type=ticket_data.get('ticket_type'),
                    price=ticket_data.get('price'),
                    available_tickets=ticket_data.get('available_tickets')
                )
                db.session.add(ticket)
                print("Added the new ticket to the session")

        # Delete tickets that were not present in the new data
        for ticket_id in existing_ticket_ids:
            ticket = Ticket.query.get(ticket_id)
            db.session.delete(ticket)

        try:
            db.session.commit()
            print("Number of tickets for the event:", len(event.tickets))
            print("Committed the session")
            return jsonify(success=True)

        except Exception as e:
            db.session.rollback()
            print("Error occurred:", str(e))
            raise e  # Re-raise the exception to see its traceback in the logs

    return jsonify(success=False)

#admin festivals
@app.route('/admin/festival')
@login_required
def festival1():
    # Assuming 'Concerts' category has id=1
    events = Event.query.filter_by(category_id=2).all()

    # Get the tickets for each event
    tickets = {event.id: Ticket.query.filter_by(event_id=event.id).all() for event in events}
    if not events:
        flash('No festivals are available, Consider adding one...!', 'info')

    return render_template('adminfestival.html', events=events, tickets=tickets)

@app.route('/admin/festival/add', methods=['POST'])
@login_required
def add_event1():
    
    if request.is_json:
        try:
            data = request.get_json()
            event = Event(
                name=data.get('name'),
                venue=data.get('venue'),
                date=datetime.strptime(data.get('start'), '%Y-%m-%dT%H:%M'),
                end=datetime.strptime(data.get('end'), '%Y-%m-%dT%H:%M'),
                description=data.get('description'),
                category_id=2,  # Assuming 'Concerts' category has id=1
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


@app.route('/admin/festival/delete/<int:event_id>', methods=['POST'])
@login_required
def delete_event1(event_id):
    event = Event.query.get(event_id)
    if event:
        db.session.delete(event)
        db.session.commit()
        return jsonify(success=True)
    return jsonify(success=False)

@app.route('/admin/festival/modify/<int:event_id>', methods=['GET'])
@login_required
def get_event_for_modify1(event_id):
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


@app.route('/admin/festival/modify/<int:event_id>', methods=['POST'])
def modify_event1(event_id):
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

        # Keep track of existing ticket ids to delete if not present in the new data
        existing_ticket_ids = [ticket.id for ticket in event.tickets]

        # Update existing tickets and create new ones
        for ticket_data in data.get('tickets', []):
            ticket_id = ticket_data.get('id')
            if ticket_id in existing_ticket_ids:
                # Update existing ticket
                ticket = Ticket.query.get(ticket_id)
                ticket.ticket_type = ticket_data.get('ticket_type', ticket.ticket_type)
                ticket.price = ticket_data.get('price', ticket.price)
                ticket.available_tickets = ticket_data.get('available_tickets', ticket.available_tickets)
                existing_ticket_ids.remove(ticket_id)
            else:
                # Create new ticket
                ticket = Ticket(
                    event_id=event.id,
                    ticket_type=ticket_data.get('ticket_type'),
                    price=ticket_data.get('price'),
                    available_tickets=ticket_data.get('available_tickets')
                )
                db.session.add(ticket)
                print("Added the new ticket to the session")

        # Delete tickets that were not present in the new data
        for ticket_id in existing_ticket_ids:
            ticket = Ticket.query.get(ticket_id)
            db.session.delete(ticket)

        try:
            db.session.commit()
            print("Number of tickets for the event:", len(event.tickets))
            print("Committed the session")
            return jsonify(success=True)

        except Exception as e:
            db.session.rollback()
            print("Error occurred:", str(e))
            raise e  # Re-raise the exception to see its traceback in the logs

    return jsonify(success=False)

@app.route('/admin/others')
@login_required
def others1():
    # Assuming 'Concerts' category has id=1
    events = Event.query.filter_by(category_id=3).all()

    # Get the tickets for each event
    tickets = {event.id: Ticket.query.filter_by(event_id=event.id).all() for event in events}
    if not events:
        flash('No other events are available, Consider adding one...!', 'info')

    return render_template('adminothers.html', events=events, tickets=tickets)

@app.route('/admin/others/add', methods=['POST'])
@login_required
def add_event2():
    
    if request.is_json:
        try:
            data = request.get_json()
            event = Event(
                name=data.get('name'),
                venue=data.get('venue'),
                date=datetime.strptime(data.get('start'), '%Y-%m-%dT%H:%M'),
                end=datetime.strptime(data.get('end'), '%Y-%m-%dT%H:%M'),
                description=data.get('description'),
                category_id=3,  # Assuming 'Concerts' category has id=1
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


@app.route('/admin/others/delete/<int:event_id>', methods=['POST'])
@login_required
def delete_event2(event_id):
    event = Event.query.get(event_id)
    if event:
        db.session.delete(event)
        db.session.commit()
        return jsonify(success=True)
    return jsonify(success=False)

@app.route('/admin/others/modify/<int:event_id>', methods=['GET'])
@login_required
def get_event_for_modify2(event_id):
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


@app.route('/admin/others/modify/<int:event_id>', methods=['POST'])
def modify_event2(event_id):
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

        # Keep track of existing ticket ids to delete if not present in the new data
        existing_ticket_ids = [ticket.id for ticket in event.tickets]

        # Update existing tickets and create new ones
        for ticket_data in data.get('tickets', []):
            ticket_id = ticket_data.get('id')
            if ticket_id in existing_ticket_ids:
                # Update existing ticket
                ticket = Ticket.query.get(ticket_id)
                ticket.ticket_type = ticket_data.get('ticket_type', ticket.ticket_type)
                ticket.price = ticket_data.get('price', ticket.price)
                ticket.available_tickets = ticket_data.get('available_tickets', ticket.available_tickets)
                existing_ticket_ids.remove(ticket_id)
            else:
                # Create new ticket
                ticket = Ticket(
                    event_id=event.id,
                    ticket_type=ticket_data.get('ticket_type'),
                    price=ticket_data.get('price'),
                    available_tickets=ticket_data.get('available_tickets')
                )
                db.session.add(ticket)
                print("Added the new ticket to the session")

        # Delete tickets that were not present in the new data
        for ticket_id in existing_ticket_ids:
            ticket = Ticket.query.get(ticket_id)
            db.session.delete(ticket)

        try:
            db.session.commit()
            print("Number of tickets for the event:", len(event.tickets))
            print("Committed the session")
            return jsonify(success=True)

        except Exception as e:
            db.session.rollback()
            print("Error occurred:", str(e))
            raise e  # Re-raise the exception to see its traceback in the logs

    return jsonify(success=False)



@app.route('/get_bookings', methods=['GET'])
@login_required
def get_bookings():
    # Get the bookings from the database
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
   

    # Convert the bookings to a list of dictionaries
    bookings_list = [{'id': booking.id, 'event': booking.event.name, 'ticket_type': booking.ticket.ticket_type if booking.ticket else 'N/A', 'number_of_tickets': booking.number_of_tickets} for booking in bookings]

    # Return the bookings as JSON
    return jsonify(bookings_list)

#tickets testing.....
@app.route('/admin/booked_tickets/concerts')
@login_required
def booked_tickets_concerts():
    return booked_tickets_by_event_type('concerts')

@app.route('/admin/booked_tickets/festivals')
@login_required
def booked_tickets_festivals():
    return booked_tickets_by_event_type('festivals')

@app.route('/admin/booked_tickets/others')
@login_required
def booked_tickets_others():
    return booked_tickets_by_event_type('others')

def booked_tickets_by_event_type(event_type):
    # Query the database for all bookings of the specified event type
    bookings = Booking.query.join(Event).join(EventCategory).filter(EventCategory.category_name == event_type)
    

    # Prepare the data for the template
    data = []
    for booking in bookings:
        ticket_type = getattr(booking.ticket, 'ticket_type', None)  # Check if ticket is not None before accessing ticket_type
        data.append({
            'booking_id': booking.id,
            'user_name': booking.user.name if booking.user else '',  # Check if user is not None before accessing name
            'event_name': booking.event.name if booking.event else '',  # Check if event is not None before accessing name
            'ticket_type': ticket_type,
            'booking_date': booking.date,
            'number_of_tickets': booking.number_of_tickets,
            'total_price': booking.total_price
        })

    if not data:
        flash('No bookings are made...!', 'info')

    return render_template(f'booked_tickets_{event_type}.html', data=data)


@app.route('/admin/booked')
def booked():
    # Replace this with your actual query to fetch recent bookings data
    recent_bookings = get_recent_bookings()

    # Prepare data for the template
    data = []
    for booking in recent_bookings:
        data.append({
            'user_name': booking.user.name,  # Assuming the User model has a 'name' attribute
            'event_type': booking.event.category.category_name,
            'event_name': booking.event.name,
            'ticket_type': booking.ticket.ticket_type,
            'booking_date': booking.date,
            'number_of_tickets': booking.number_of_tickets
        })

    return render_template('booked.html', data=data)


def get_recent_bookings():
    return Booking.query.order_by(Booking.date.desc()).limit(5).all()


@app.route('/admin/reviews/concerts')
@login_required
def reviews_concerts():
    return reviews_by_event_type('concerts')

@app.route('/admin/reviews/festivals')
@login_required
def reviews_festivals():
    return reviews_by_event_type('festivals')

@app.route('/admin/reviews/others')
@login_required
def reviews_others():
    return reviews_by_event_type('others')

def reviews_by_event_type(event_type):
    # Query the database for all reviews of the specified event type
    reviews = Review.query.join(Event).join(EventCategory).filter(EventCategory.category_name == event_type)

    # Prepare the data for the template
    data = []
    for review in reviews:
        data.append({
            'review_id': review.id,
            'user_name': review.user.name if review.user else '',  # Check if user is not None before accessing name
            'event_name': review.event.name if review.event else '',  # Check if event is not None before accessing name
            'review_date': review.review_date,
            'rating': review.rating,
            'review_text': review.review_text
        })
    if not data:
        flash('No reviews are posted.', 'info')

    return render_template(f'reviews_{event_type}.html', data=data)



@app.route('/admin/users')
@login_required
def admin_users():
    users = User.query.all()

    data = []
    for user in users:
        data.append({
            'user_id': user.id,
            'user_name': user.name,
            'user_email': user.email,
            'registered_on': user.registeredon.strftime('%Y-%m-%d %H:%M:%S') if user.registeredon else ''
        })

    if not data:
        flash('No users available.', 'info')

    return render_template('registered_users.html', data=data)

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required  # Add the appropriate login_required decorator
def delete_user(user_id):
    user = User.query.get(user_id)

    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    else:
        flash('User not found!', 'error')

    return redirect(url_for('admin_users'))  # Redirect to the user directory page


app.run(debug=True)
