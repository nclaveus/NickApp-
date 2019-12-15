import os
from cv2 import cv2
import numpy as np
from PIL import Image

recognizer=cv2.face.LBPHFaceRecognizer_create()
path='static\\dataset'

def getImagesId(path):
	imagePaths=[os.path.join(path,f) for f in os.listdir(path)]
	#print imagePaths
	faces=[]
	IDs=[]
	counter = 0
	for imagePath in imagePaths:
		for im in os.listdir(imagePath):
			if(counter>100):
				continue
			else:
				counter += 1
			faceImg=Image.open(os.path.join(imagePath,im)).convert('L');
			faceNP=np.array(faceImg,'uint8')
			ID=int(os.path.split(os.path.join(imagePath,im))[-1].split('.')[0])
			faces.append(faceNP)
			IDs.append(ID)
			#cv2.imshow("training", faceNP)
			#cv2.waitKey(10)
		counter = 0
	return np.array(IDs), faces 

IDs, faces=getImagesId(path)
recognizer.train(faces,np.array(IDs))
recognizer.save('recognizer1/trainingModel.yml')
cv2.destroyAllWindows()