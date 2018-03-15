from flask import Flask, render_template, flash, redirect, request, url_for, session, logging
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

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

    def __init__(self,first_name,last_name,username,email,password):
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.email = email
        self.password = sha256_crypt.encrypt(str(password))

    def __repr__(self):
        return '<User %r>' % self.username


#new_user = User('John', 'Doe', 'aDeer','aDeer@gmail.com', 'aFemaleDeer')
#db.session.add(new_user);
#db.session.commit();

#The home page
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

#Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.first_name.data,form.last_name.data,form.username.data,form.email.data,form.password.data)
        db.session.add(user)
        db.session.commit()
        db.session.close()

        flash('You are now registered and can now login')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

#Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #get from forms
        username = request.form['username']
        password_candidate = request.form['password']
        result = User.query.filter_by(username = username).first()

        if result:
            password = result.password
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                print('suceeded')
                return redirect(url_for('search'))
            else:
                error = 'Invalid login'
                print('invalid password')
                return render_template('login.html', error=error)
            db.session.close()
        else:
            error = 'Username not found'
            print('invalid password')
            return render_template('login.html', error=error)
    return render_template('login.html')

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out, error')
    return redirect(url_for('login'))

@app.route('/search')
@is_logged_in
def search():
    return render_template('search.html')

if __name__ == '__main__':
    app.secret_key='skeletonk!'
    app.run(debug=True)
