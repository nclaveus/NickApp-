from flask import Flask,render_template,request,session,logging,url_for,redirect, flash, Response
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session,sessionmaker
from passlib.hash import sha256_crypt
from flask_mysqldb import MySQL
from cv2 import cv2
import numpy as np
import pickle
import os

face_cascade = cv2.CascadeClassifier('cascades/data/haarcascade_frontalface_alt2.xml')
(width, height) = (130, 100)



app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'Nickappdb'

mysql = MySQL(app)


cap = cv2.VideoCapture(0)

from random import randint

def write_faceid(face_id):
    with open("face_id.tmp","wb") as fd:
        pickle.dump(face_id, fd)
def read_faceid():
    if(os.path.exists("face_id.tmp")):
        return pickle.load(open("face_id.tmp","rb"))
    else:
        return ""

def random_tokenize(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)


def check():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("recognizers/trainner.yml")
    gray = cv2.imread("demo.jpg",0)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=4)
    for (x,y,w,h) in faces:
        #print(x,y,w,h) 
        roi_gray = gray[y:y+h, x:x+w]
        id_,conf = recognizer.predict(roi_gray)
        if(conf>0.9):
            with open("pickles/face-labels.pickle", 'rb') as f:
                og_labels = pickle.load(f)
                id_ = list(og_labels.keys())[list(og_labels.values()).index(id_)]
            return str(id_)
    return "0"

def save_vars(ob):
    with open("vars.pickle","wb") as f:
        f.truncate(0)
        pickle.dump(ob,f)
def load_vars():
    import os.path
    if(os.path.exists('vars.pickle')):
        if os.path.getsize('vars.pickle') > 0: 
            with open("vars.pickle","rb") as f:
                return pickle.load(f)
    else:
        save_vars([0,False,400,"image_saved"])
        return load_vars()

@app.route("/")
def hom():
    return render_template("home.html")

    #register form

@app.route("/register", methods=["GET","POST"])
def register():
    f = open("vars.pickle","wb")
    f.truncate(0)
    pickle.dump([0,False,400,"image_saved"],f)
    f.close()
    if request.method == "POST":
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        vars = load_vars()
        print(vars)
        avatarimg = "static/dataset/"+vars[3]+"/"+str(vars[0])+'.jpg'
        #face_id = vars[3]
        secure_password = sha256_crypt.encrypt(str(password))
        
        if password == confirm:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users(firstname, lastname, username, password, avatarimg, face_id) VALUES (%s, %s, %s, %s, %s, %s)", (firstname, lastname, username, secure_password, avatarimg, read_faceid()))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('information'))
        else:
            flash("Le password ne correspond pas","danger")
            return render_template("register.html")
    return render_template("register.html")



def gen():
    
   while True:
        ret, frame = cap.read()
       
        if not ret:
            print("Error: failed to capture image")
            break
        
        cv2.imwrite('demo.jpg', frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=4)
        
        for (x,y,w,h) in faces:
            print(x,y,w,h) 
            roi_gray = gray[y:y+h, x:x+w]
           
        vars = load_vars()
        if(vars[1]):
            if(not os.path.exists("static/dataset/"+read_faceid())):
                os.makedirs("static/dataset/"+read_faceid())
            cv2.imwrite("static/dataset/"+read_faceid()+"/"+str(vars[0])+'.jpg', roi_gray)
            print("okie")
            if(vars[0]<vars[2]):
                vars[0]+=1
                print("saving state : "+str(vars[0]))
            else:
                vars[1] = False
                print("finished"+str(vars[0])+" , "+str(vars[1]))
                write_faceid(vars[3])
        save_vars(vars)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + open('demo.jpg', 'rb').read() + b'\r\n')


@app.route('/video_feed')
def video_feed():
     
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/saveimg')
def saving():
    firstn = request.args.get('firstn')
    lastn = request.args.get('lastn')
    token = request.args.get('token')
    vars = load_vars()
    vars[1]=True
    vars[3] = firstn+"_"+lastn+"_"+token
    save_vars(vars)
    print("launched")
    write_faceid(firstn+"_"+lastn+"_"+token)
    return "ok"
@app.route('/facecheck')
def facecheck():
    # lis image tmp_face.jpg
    # chercher_correspondance chercher qqun X a qui correspond la face temporaire
    # X
    #label,prob = check(cv2.imread("tmp_face.jpg"))
    #if(prob>0.6):
    #    return label+"1"
    #else:
    #    return 0

    # si trouve (X)
    # alors return [X+1]
    # sinon return 0
    print(check())
    return check()



@app.route("/information")
def information():
    return render_template("information.html")




@app.route("/login",  methods=["GET", "POST"])
def login():
    if request.method == "POST" :
        password = request.form["password"]
        face_id = request.form["face_id"]
        print(face_id)
        cur = mysql.connection.cursor()
        passworddata = cur.execute('SELECT password FROM users WHERE face_id = "'+face_id+'"')
        passworddata = cur.fetchone()
        print("le passsword est : "+str(passworddata))
        if(passworddata is None):
            flash("vous ne pouvez pas connecter, le password ne correspond pas","danger")
            return render_template("home.html")
        # Fetch one record and return result
        for password_data in passworddata:
            if sha256_crypt.verify(password, password_data):
                flash("Vous etes connecter maintenant","success")
                return render_template("information.html")
            else:
                flash("vous ne pouvez pas connecter, le password ne correspond pas","danger")
                return render_template("login.html")

    return render_template("login.html")

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("recognizers/trainner.yml")

labels = {"person_name": 1}
with open("pickles/face-labels.pickle", 'rb') as f:
	og_labels = pickle.load(f)
	labels = {v:k for k,v in og_labels.items()}


def camera():
   
   while True:
        ret, frame = cap.read()
       
        if not ret:
            print("Error: failed to capture image")
            break
        cv2.imwrite('demo.jpg', frame)

        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=4)
        for (x, y, w, h) in faces:
            #print(x,y,w,h)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]

            id_, conf = recognizer.predict(roi_gray)
            if conf>=4 and conf <= 85:
                #print(id_)
                #print(labels[id_])
                font = cv2.FONT_HERSHEY_SIMPLEX
                name = labels[id_]
                color = (255, 255, 255)
                stroke = 2
                cv2.putText(frame, name, (x,y), font, 1, color, stroke, cv2.LINE_AA)
        
            img_item = "7.jpg"
            cv2.imwrite(img_item, roi_color)
            
            color = (255, 0, 0) #BGR 0-255 
            stroke = 2
            end_cord_x = x + w
            end_cord_y = y + h
            cv2.rectangle(frame, (x, y), (end_cord_x, end_cord_y), color, stroke)
        cv2.imwrite('demo.jpg', frame)
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + open('demo.jpg', 'rb').read() + b'\r\n')


@app.route('/came_feed')
def came_feed():
     
    return Response(camera(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__=="__main__":
    app.secret_key="ma soeur"
    app.run(debug=True)