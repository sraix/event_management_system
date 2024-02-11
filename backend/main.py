
from flask import Flask, redirect, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
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

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/userlogin")
def userlogin():
    return render_template("userlogin.html")

@app.route("/usersignup")
def usersignup():
    return render_template("usersignup.html")

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



@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get("password")
        user_record = users.query.filter_by(email=email).first()

        if user_record and check_password_hash(user_record.password, password):
            login_user(user_record)
            flash("Login Success", "info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials", "danger")
            return render_template("userlogin.html")

    return render_template("userlogin.html")

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
