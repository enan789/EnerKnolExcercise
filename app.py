from flask import Flask, render_template, flash, redirect, request, url_for, session, logging
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:wordpass@localhost/flaskapp"
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column('id', db.Integer, primary_key=True)
    username = db.Column('username', db.String(30), primary_key=False)
    first_name = db.Column('first_name', db.String(100), primary_key=False)
    last_name = db.Column('last_name', db.String(100), primary_key=False)
    username = db.Column('username', db.String(30), unique=True)
    email = db.Column('email', db.String(100), unique=True)
    password = db.Column('password', db.String(100), primary_key=False)

    def __init__(self,id,first_name,last_name,username,email,password):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.email = email
        self.password = sha256_crypt.encrypt(str(password))

    def __repr__(self):
        return '<User %r>' % self.username


#new_user = User(1,'John', 'Doe', 'aDeer','aDeer@gmail.com', 'aFemaleDeer')
#db.session.add(new_user);
#db.session.commit();

@app.route('/')
def index():
    return render_template('index.html')

class RegisterForm(Form):
    username = StringField('Username', [validators.Length(min=6, max=25)])
    first_name = StringField('First Name', [validators.Length(min=1, max=50)])
    last_name = StringField('Last Name', [validators.Length(min=1, max=50)])
    email = StringField('Email', [validators.Length(min=1, max=50)])
    password = PasswordField('Password', [
    validators.DataRequired(),
    validators.EqualTo('confirm', message = 'Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        db.session.add(form)
        db.session.commit()

        return render_template('register.html')
    return render_template('register.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
