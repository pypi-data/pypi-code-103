import nltk
import numpy as np
import random
import string
import cv2
import os
#from cvzone.HandTrackingModule import HandDetector

cascPath=os.path.dirname(cv2.__file__)+"/data/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascPath)



from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

lemmer = nltk.stem.WordNetLemmatizer()
def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]

remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)

def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))


# Generating response
def response(user_input, filename = "info.txt"):
    f = open(filename, 'r', errors='ignore')
    raw = f.read()
    raw = raw.lower()
    sent_tokens = nltk.sent_tokenize(raw)
    sent_tokens.append(user_input)
    
    robo_response=''
    TfidfVec = TfidfVectorizer(tokenizer=LemNormalize)
    tfidf = TfidfVec.fit_transform(sent_tokens)
    vals = cosine_similarity(tfidf[-1], tfidf)
    idx=vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-2]
    if(req_tfidf==0):
        #robo_response=robo_response+"I am sorry! I don't understand you"
        #robo_response = robo_response + "Please train me on this"
        print("I am sorry! I don't understand you.Please train me on this")
        train_input = input("enter the information : ")
        f = open(filename, "a")
        f.write("\n")
        f.write(train_input+".")
        f.close()
        robo_response = robo_response+"Thanks for training me..I am ready now"
        return robo_response
    else:
        robo_response = robo_response+sent_tokens[idx]
        return robo_response

def guiresponse(user_input, filename = "info.txt"):
    f = open(filename, 'r', errors='ignore')
    raw = f.read()
    raw = raw.lower()
    sent_tokens = nltk.sent_tokenize(raw)
    sent_tokens.append(user_input)
    
    robo_response=''
    TfidfVec = TfidfVectorizer(tokenizer=LemNormalize)
    tfidf = TfidfVec.fit_transform(sent_tokens)
    vals = cosine_similarity(tfidf[-1], tfidf)
    idx=vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-2]
    if(req_tfidf==0):
        robo_response=robo_response+"I am sorry! I don't understand you"
        robo_response = robo_response + "Please train me on this"
        #print("I am sorry! I don't understand you.Please train me on this")
        #train_input = input("enter the information : ")
        flag=1
        return robo_response
    else:
        robo_response = robo_response+sent_tokens[idx]
        return robo_response

def convert2Gray(frame):
    outFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return outFrame


def detectface(frame):

    faces = faceCascade.detectMultiScale(
        frame,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    return faces

def drawBox(frame,faces):

    if len(faces) == 0:
        faces = [[0,0,0,0]]

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    return frame,x,y

def writeText(frame,text,x,y,R,G,B):

    cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (R, G, B), 2)
    return frame
    

def startCamera(num):
    vid = cv2.VideoCapture(num)
    return vid

def stopCamera(vid):
    vid.release()

def displayImage(name,frame):
    cv2.imshow(name,frame)


def saveImage(fileloc,frame):
    cv2.imwrite(fileloc,frame)
    

def closewindow():
    cv2.destroyAllWindows()
"""
def detectHand(frame):
    detector = HandDetector(detectionCon=0.8, maxHands=2)
    
    
    hands, frame = detector.findHands(frame)
    
    if hands:
        # Hand 1
        hand1 = hands[0]
        lmList1 = hand1["lmList"]  # List of 21 Landmark points
        bbox1 = hand1["bbox"]  # Bounding box info x,y,w,h
        centerPoint1 = hand1['center']  # center of the hand cx,cy
        handType1 = hand1["type"]  # Handtype Left or Right

        fingers1 = detector.fingersUp(hand1)
        totalFingers1 = fingers1.count(1)
        cv2.putText(frame, f'Fingers:{totalFingers1}', (bbox1[0] + 200, bbox1[1] - 30),
                    cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

    else:
        totalFingers1 = 0


    if len(hands) == 2:
        # Hand 2
        hand2 = hands[1]
        lmList2 = hand2["lmList"]  # List of 21 Landmark points
        bbox2 = hand2["bbox"]  # Bounding box info x,y,w,h
        centerPoint2 = hand2['center']  # center of the hand cx,cy
        handType2 = hand2["type"]  # Hand Type "Left" or "Right"

        fingers2 = detector.fingersUp(hand2)
        totalFingers2 = fingers2.count(1)
        cv2.putText(frame, f'Fingers:{totalFingers2}', (bbox2[0] + 200, bbox2[1] - 30),
                    cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
    else:
        totalFingers2 = 0
            
    
    
    return frame,totalFingers1,totalFingers2

 """   
