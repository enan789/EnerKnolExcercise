from flask import Flask, render_template, flash, redirect, request, url_for, session, logging
from flask_pymongo import PyMongo
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from elasticsearch import Elasticsearch
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:wordpass@localhost/flaskapp"
db = SQLAlchemy(app)

app.config['MONGO_DBNAME'] = "items"
app.config['MONGO_URI'] = "mongodb://testing:1234@ds149934.mlab.com:49934/items"
mongo = PyMongo(app)
es = Elasticsearch('localhost:9200',use_ssl=False,verify_certs=True)

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

class Item():
    _id = ''
    name = ''
    description = ''
    def __init__(self,_id,name,description):
        self._id = _id
        self.name = name
        self.description = description


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

def paginate_data(array,page_size,page):
    return array[page_size*(page-1):page_size*page]

def get_data():
    itemsDB = mongo.db.EnerknolVals
    items = itemsDB.find()
    return items

#Tried to input mongodb data into search but failed to do so
def search(items):
    itemsES = []
    for item in items:
        itemsES.append({ '_id' : str(item['_id'].ObjectId()), 'name' : item['name'], 'description' : item["description"]})
        res = es.index(index="test-index", doc_type='document', id=1, body=itemsES)
        res = es.get(index="test-index", doc_type='document', id=1)

        es.indices.refresh(index="test-index")

        res = es.search(index="test-index", body={"query": {"match_all": {}}})
        print("Got %d Hits:" % res['hits']['total'],file=sys.stdout)
        return render_template('search.html', items = res['hits']['hits'])

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
                return redirect('list/1')
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



@app.route('/list/<int:page>')
@is_logged_in
def search(page):
    items = get_data()
    page_size = 3

    return render_template('search.html', items = paginate_data(items,page_size,page), page_size= page_size)

@app.route('/item_page')
@is_logged_in
def item_page():
    val = request.args.get('val', None)
    return render_template('item_page.html', val=val)

if __name__ == '__main__':
    app.secret_key='skeletonk!'
    app.run(debug=True)
