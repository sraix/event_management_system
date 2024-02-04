from flask import Flask,redirect,render_template
from flask_sqlalchemy import SQLAlchemy
# mydatabase connection
local_server=True
app=Flask(__name__)
app.secret_key="sraix"

app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/ems'
db = SQLAlchemy(app)



@app.route("/")
def home():
    return render_template("index.html")
#testing db connected or not
@app.route("/test")
def test():
    return render_template("index.html")
app.run(debug=True)
