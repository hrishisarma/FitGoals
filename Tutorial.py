from fabric.context_managers import settings
from fabric.operations import sudo, run
from fabric.state import env
from flask import Flask, render_template, request, session, url_for,redirect, jsonify, json
from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt

app = Flask(__name__)
app.secret_key = 'super secret key'

client = MongoClient('mongodb://dugi:hello123@ds161225.mlab.com:61225/players1993')
db = client['players1993']

@app.route('/')
def index():
    if session.get('logged_in'):
        name = session['username']
        return render_template('list.html', name=name)

    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    users = db.users
    login_users = users.find_one({'name': request.form['user']})

    if login_users:
            if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_users['pass'].encode('utf-8'))== login_users['pass'].encode('utf-8'):
                session['username'] = request.form['user']
                session['logged_in'] = True
                return redirect(url_for('index'))

            return 'Invalid username/password combination'


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = db.users
        existing_user = users.find_one({'name': request.form['user']})



        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name' : request.form['user'], 'pass': hashpass})
            session['username'] = request.form['user']
            return redirect(url_for('index'))
        return 'Username exists'

    return render_template('register.html')
@app.route('/ok')
def ok():
    return render_template('ok.html')

@app.route('/logout')
def logout():
    session['logged_in'] = False
    return index()

@app.route('/add')
def add():
    user = db.db.users
    user.insert({'name': 'gandu'})
    return 'Added User!'

@app.route('/delete')
def delete():
    user = db.db.users
    a = user.find_one({'name': 'gandu'})
    user.remove(a)
    return 'Removed Hrishi'

@app.route("/addMachine", methods=['POST'])
def addMachine():
    try:
        json_data = request.json['info']
        deviceName = json_data['device']
        ipAddress = json_data['ip']
        userName = json_data['username']
        password = json_data['password']
        portNumber = json_data['port']

        db.db.insert_one({
            'name': session['username'], 'device': deviceName, 'ip': ipAddress, 'username': userName, 'password': password, 'port': portNumber
        })
        return jsonify(status='OK', message='inserted successfully')

    except Exception, e:
        return jsonify(status='ERROR', message=str(e))


@app.route('/getMachine', methods=['POST'])
def getMachine():
    try:
        machineId = request.json['id']
        machine = db.db.find_one({'_id': ObjectId(machineId)})
        machineDetail = {
            'device': machine['device'],
            'ip': machine['ip'],
            'username': machine['username'],
            'password': machine['password'],
            'port': machine['port'],
            'id': str(machine['_id'])
        }
        return json.dumps(machineDetail)
    except Exception, e:
        return str(e)


@app.route('/updateMachine', methods=['POST'])
def updateMachine():
    try:
        machineInfo = request.json['info']
        machineId = machineInfo['id']
        device = machineInfo['device']
        ip = machineInfo['ip']
        username = machineInfo['username']
        password = machineInfo['password']
        port = machineInfo['port']

        db.db.update_one({'_id': ObjectId(machineId)}, {
            '$set': {'device': device, 'ip': ip, 'username': username, 'password': password, 'port': port}})
        return jsonify(status='OK', message='updated successfully')
    except Exception, e:
        return jsonify(status='ERROR', message=str(e))


@app.route("/getMachineList1", methods=['POST'])
def getMachineList1():
    try:
        machines = db.db.find()

        machineList = []
        for machine in machines:
            print machine
            machineItem = {
                'device': machine['device'],
                'ip': machine['ip'],
                'username': machine['username'],
                'password': machine['password'],
                'port': machine['port'],
                'id': str(machine['_id'])
            }
            machineList.append(machineItem)
    except Exception, e:
        return str(e)
    return json.dumps(machineList)

@app.route("/getMachineList", methods=['POST'])
def getMachineList():
    try:
        ok=session['username']
        machines = db.db.find({'name': ok})

        machineList = []
        for machine in machines:
            print machine
            machineItem = {
                'device': machine['device'],
                'ip': machine['ip'],
                'username': machine['username'],
                'password': machine['password'],
                'port': machine['port'],
                'id': str(machine['_id'])
            }
            machineList.append(machineItem)
    except Exception, e:
        return str(e)
    return json.dumps(machineList)

@app.route("/getfriendshowlist", methods=['POST'])
def getfriendshowlist():
    try:
        machines = db.db.find()

        machineList = []
        for machine in machines:
            print machine
            machineItem = {
                'device': machine['device'],
                'ip': machine['ip'],
                'username': machine['username'],
                'password': machine['password'],
                'port': machine['port'],
                'id': str(machine['_id'])
            }
            machineList.append(machineItem)
    except Exception, e:
        return str(e)
    return json.dumps(machineList)

@app.route("/getFriend", methods=['POST'])
def getFriend():
    try:
        json_data = request.json['info']
        deviceName = json_data['name2']

        names=db.users.find({
            'name': deviceName,
        })
        machineList = []
        for machine in names:
            print machine
            machineItem = {
                'name': machine['name'],
                'password': machine['pass'],

            }
            machineList.append(machineItem)
    except Exception, e:
         return str(e)
    return json.dumps(machineList)

@app.route("/execute", methods=['POST'])
def execute():
    try:
        machineInfo = request.json['info']
        ip = machineInfo['ip']
        username = machineInfo['username']
        password = machineInfo['password']
        command = machineInfo['command']
        isRoot = machineInfo['isRoot']

        env.host_string = username + '@' + ip
        env.password = password
        resp = ''
        with settings(warn_only=True):
            if isRoot:
                resp = sudo(command)
            else:
                resp = run(command)

        return jsonify(status='OK', message=resp)
    except Exception, e:
        print 'Error is ' + str(e)
        return jsonify(status='ERROR', message=str(e))


@app.route("/deleteMachine", methods=['POST'])
def deleteMachine():
    try:
        machineId = request.json['id']
        db.db.remove({'_id': ObjectId(machineId)})
        return jsonify(status='OK', message='deletion successful')
    except Exception, e:
        return jsonify(status='ERROR', message=str(e))


if __name__ == '__main__':
    app.run(debug=True)
