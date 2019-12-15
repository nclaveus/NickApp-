#from urllib3
#import urllib.requests     
from cv2 import cv2
import numpy as np


#url='http://192.168.43.1:8080/shot.jpg'
#url='http://192.168.216.101:8080/shot.jpg'

faceDetect=cv2.CascadeClassifier('cascade/haarcascade_frontalface_default.xml');
cam=cv2.VideoCapture(0)
font = cv2.FONT_HERSHEY_SIMPLEX

recono=cv2.face.LBPHFaceRecognizer_create()
recono.read("recognizer1/trainingModel.yml");
id=0;
nom="";
while(True):
    ret,img=cam.read();
    #imgResp=urllib.request.urlopen(url);
    #imgNp=np.array(bytearray(imgResp.read()),dtype=np.uint8)
    #img=cv2.imdecode(imgNp,-1)

    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    faces=faceDetect.detectMultiScale(gray,1.3,5);
    for(x,y,w,h) in faces:
        cv2.rectangle(img, (x,y),(x+w,y+h), (255,255,255),4)
        id, conf=recono.predict(gray[y:y+h, x:x+w]);
        if(id==2):
            nom="Obed Meralus" 
        elif(id==3):
            nom="Gregory "
        elif(id==8):
            nom="Rooldy"
        elif(id==5):
            nom="Taliban"
        elif(id==16):
            nom="Roc Nail"
        elif(id==1):
            nom="Benson Louis"
        elif(id==15):
            nom="Nick"
        elif(id==12):
            nom="UNKNOWN"
        else :
            nom="unknown"
        cv2.putText(img,str(nom),(x,y-10),font,1,(0,255,255),2)
    ims = cv2.resize(img, (760, 440))
    cv2.imshow("Face Detection",ims);
    if(cv2.waitKey(1)==ord('q')):
        break;
#cam.release()
cv2.destroyAllWindows()