from flask import Flask, redirect, render_template, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask.helpers import url_for
from flask_login import UserMixin, login_required, logout_user, login_user, LoginManager, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, text

# mydatabase connection
local_server = True
app = Flask(__name__)
app.secret_key = "sraix"

# this is for getting unique user access
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "userlogin"

#app.config
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/ems'
db = SQLAlchemy(app)

@login_manager.user_loader
def load_user(userid):
    return users.query.get(int(userid))

@login_manager.user_loader
def load_user(username):
    return admins.query.get(username)

# users  table in the database
class users(UserMixin, db.Model):
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    email = db.Column(db.String(20))
    password = db.Column(db.String(1000))
    def get_id(self):
        return str(self.userid)

# admin table to handle admin related tasks
class admins(UserMixin, db.Model):
    username = db.Column(db.String(20),primary_key=True)
    email=db.Column(db.String(20))
    password = db.Column(db.String(20))
    def get_id(self):
        return str(self.username)

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
            admin_record = admins.query.filter_by(email=session['email']).first()
            if admin_record:
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
        admin_record = admins.query.filter_by(email=email).first()
        admin_record1=admins.query.filter_by(password=password).first()
        if admin_record and admin_record1:
            login_user(admin_record)
            session['logged_in'] = True
            session['email'] = email
            session['username'] = admin_record.username
            session['user_type'] = 'admin'  # Set user type
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


@app.route('/adddata', methods=["POST", "GET"])
def adddata():
    if('user' in session and session['username']==admins['username']):
        if request.method == "POST":
            pass
        return render_template( 'adddata.html' )
    else:
        flash("Login and try again!","primary")
        return redirect("/admin")

#just testing


#database intiating
class events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    venue = db.Column(db.String(100))
    date = db.Column(db.DateTime)
    description = db.Column(db.String(1000))
    ticketprice = db.Column(db.String(11))
    type = db.Column(db.Integer)




@app.route('/user/concerts')
@login_required
def concerts():
    concerts = events.query.filter_by(type=1).all()
    return render_template('concerts.html', events=concerts)

@app.route('/user/festivals')
@login_required
def festivals():
    festivals = events.query.filter_by(type=2).all()
    return render_template('festivals.html', events=festivals)

@app.route('/user/others')
@login_required
def others():
   # others = events.query.filter_by(type=3).all()
    return render_template('index.html')#events=others

@app.route('/user/concerts/buy_ticket/<int:event_id>', methods=['POST'])
@login_required
def buy_ticket(event_id):
    new_ticket = Ticket(event_id=event_id, user_id=current_user.id)
    db.session.add(new_ticket)
    db.session.commit()
    return redirect(url_for('concerts'))

app.run(debug=True)
