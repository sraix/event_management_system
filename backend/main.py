
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
login_manager = LoginManager(app)
login_manager.login_view = "login"

#app.config
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/ems'
db = SQLAlchemy(app)


@login_manager.user_loader
def load_user(userid):
    return users.query.get(userid)

@login_manager.user_loader
def load_user(username):
    return admins.query.get(username)

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

class users(UserMixin, db.Model):
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    email = db.Column(db.String(20))
    password = db.Column(db.String(1000))

    def get_id(self):
        return str(self.userid)
    
class admins(UserMixin, db.Model):
    
    username = db.Column(db.String(20),primary_key=True)
    email=db.Column(db.String(20))
    password = db.Column(db.String(20))
    

    def get_id(self):
        return str(self.username)

@app.route("/")
def home():
    return render_template("homepage.html")



@app.route("/userlogin")
def userlogin():
    return render_template("userlogin.html")

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


#user login
@app.route('/userlog', methods=["POST", "GET"])
def userlog():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get("password")
        user_record = users.query.filter_by(email=email).first()

        if user_record and check_password_hash(user_record.password, password):
            login_user(user_record)
            flash("Login Success", "info")
            return redirect(url_for("user"))
            
        else:
            flash("Invalid Credentials", "danger")
            return render_template("userlogin.html")

    return render_template("userlogin.html")

@app.route('/user')

def user():
    if not session.get('logged_in'):
        return redirect(url_for('userlogin'))
    else:
        return render_template('user.html')

#admin login


@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get("password")
        admin_record = admins.query.filter_by(username=username).first()
        admin_record1=admins.query.filter_by(password=password).first()
        if admin_record and admin_record1:
            login_user(admin_record)
            session['logged_in'] = True
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
    flash("Logout Successfull","warning")
    return redirect("/")

@app.route('/logoutadmin')
def logoutadmin():
    logout_user()
    flash("Admin, You are logged out!", "primary")
    return redirect('/')

@app.route('/adddata', methods=["POST", "GET"])
def adddata():
    if('user' in session and session['username']==admins['username']):
        if request.method == "POST":
            pass
        return render_template( 'adddata.html' )
    else:
        flash("Login and try again!","primary")
        return redirect("/admin")



#testing db connected or not
@app.route("/test")
def test():
    try:
        a = Test.query.all()
        print(a)
        return 'MY DATABASE IS CONNECTED'
    except Exception as e:
        print(e)
        return 'NOT CONNECTED'

app.run(debug=True)
