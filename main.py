import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from flask import Flask,render_template,request,jsonify,make_response
import jwt
import datetime
from functools import wraps

cred = credentials.Certificate(r"C:\Users\siddh\OneDrive\Desktop\serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db=firestore.client()

app=Flask(__name__)

app.config['SECRET_KEY']='randomsecretkey'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return jsonify({'message' : 'Token is missing!'})

        try: 
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message' : 'Token is invalid!'})

        return f(*args, **kwargs)

    return decorated

# @app.route('/unprotected')
# def unprotected():
#     return jsonify({'message':'Anyone can view this'})

# @app.route('/protected')
# @token_required
# def protected():
#     return jsonify({'message':'This is only avaliable for people with valid tokens'})

@app.route('/login')
def login():
    auth=request.authorization
    if auth and auth.password=='password':
        token=jwt.encode({'user':auth.username,'exp':datetime.datetime.utcnow()+datetime.timedelta(seconds=30)},app.config['SECRET_KEY'])
        return jsonify({'token':token.decode('UTF-8')})
    
    return make_response('Could not verify!',401,{'WWW-Authenticate':'Basic realm="Login Required"'})

#BASIC AUTHENTICATION
# @app.route('/')
# def home():
#     if request.authorization and request.authorization.username=='username' and request.authorization.password=='password':
#         return "You are logged in!"
    
#     return make_response('Could not verify!', 401, {'WWW-Authenticate':'Basic realm="Login Required"'})

@app.route('/create/<name>/<age>/<loc>',methods=['GET','POST'])
@token_required
def create(name,age,loc):
    db.collection('employees').add({'name':name, 'age':age, 'loc': loc})
    return "created"

@app.route('/update/<name>',methods=['GET','POST'])
@token_required
def update(name):
    docs=db.collection('employees').get()
    for doc in docs:
        if doc.to_dict()["name"]==name:
            key = doc.id
            db.collection('employees').document(key).update({"loc":"chennai"})
    return "document with name "+name+" updated"

@app.route('/delete/<age>',methods=['GET','POST'])
@token_required
def delete(age):
    docs=db.collection('employees').get()
    for doc in docs:
        if doc.to_dict()["age"]==int(age):
            key=doc.id
            db.collection('employees').document(key).delete()
            return "document with key "+key+" deleted"
        return "no such record"

@app.route('/deleteAll',methods=['GET','POST'])
@token_required
def deleteAll():
    docs=db.collection('employees').get()
    for doc in docs:
        key=doc.id
        db.collection('employees').document(key).delete()
    return "deleted all"

@app.route('/list',methods=['GET','POST'])
def listAll():
    docs=db.collection('employees').get()
    res=[]
    for doc in docs:
        res.append(doc.to_dict())
    return jsonify(res)

@app.route('/filter',methods=['GET','POST'])
def filter():
    docs=db.collection('employees').get()
    res=[]
    for doc in docs:
        if doc.to_dict()["loc"]=="Hyderabad":
            res.append(doc.to_dict())
    return jsonify(res)

if __name__ == '__main__':
    app.run(debug=True)
