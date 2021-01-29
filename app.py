import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from flask import Flask,render_template,request,jsonify,make_response

cred = credentials.Certificate(r"C:\Users\siddh\OneDrive\Desktop\serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db=firestore.client()

app=Flask(__name__)

@app.route('/')
def home():
    return "WELCOME!"

@app.route('/<name>/<pwd>',methods=['GET'])
def auth(name,pwd):
    if name=="sid" and pwd=="12345":
        return "you have logged in"
    return "not authorized"

@app.route('/create/<name>/<age>/<loc>',methods=['GET','POST'])
def create(name,age,loc):
    db.collection('employees').add({'name':name, 'age':age, 'loc': loc})
    return "created"

@app.route('/update/<name>',methods=['GET','POST'])
def update(name):
    docs=db.collection('employees').get()
    for doc in docs:
        if doc.to_dict()["name"]==name:
            key = doc.id
            db.collection('employees').document(key).update({"loc":"chennai"})
    return "document with name "+name+" updated"

@app.route('/delete/<age>',methods=['GET','POST'])
def delete(age):
    docs=db.collection('employees').get()
    for doc in docs:
        if doc.to_dict()["age"]==int(age):
            key=doc.id
            db.collection('employees').document(key).delete()
            return "document with key "+key+" deleted"
        return "no such record"

@app.route('/deleteAll',methods=['GET','POST'])
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
