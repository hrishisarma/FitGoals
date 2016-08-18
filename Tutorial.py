from flask import Flask, render_template, request, session, url_for,redirect
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
app.secret_key = 'super secret key'

client = MongoClient('mongodb://dugi:hello123@ds161225.mlab.com:61225/players1993')
db = client['players1993']

@app.route('/')
def index():
    if 'username' in session:
        return 'you are logged in as ' + session['username']

    return render_template('index.html')

@app.route('/login', methods=['POST','GET'])
def login():
    login_users = db.db.users
    login_users.find_one({'name' : request.form['user']})

    if login_users:
            if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_users['pass'].encode('utf-8'))== login_users['pass'].encode('utf-8'):
                session['username'] = request.form['user']
            return redirect(url_for('index'))

    return 'Invalid username/password combination'

    return render_template('register.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = db.db.users
        existing_user = users.find_one({'name' : request.form['user']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'),bcrypt.gensalt())
            users.insert({'name' : request.form['user'], 'pass' : hashpass})
            session['username'] = request.form['user']
            return redirect(url_for('index'))
        return 'Username exists'

    return render_template('register.html')



@app.route('/add')
def add():
    user = db.db.users
    user.insert({'name' : 'gandu'})
    return 'Added User!'

@app.route('/delete')
def delete():
    user = db.db.users
    a = user.find_one({'name' : 'gandu'})
    user.remove(a)
    return 'Removed Hrishi'

if __name__ == '__main__':
    app.run(debug=True)
