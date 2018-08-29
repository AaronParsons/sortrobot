import cv2, imutils, os, time

CASCADE_MTG_BACK = 'data/cascades/cascade_mtg_back003.xml'
W,H = 48,36

MTG_BACK_CLASSIFIER = cv2.CascadeClassifier(CASCADE_MTG_BACK)

def read_webcam(to_file, brightness=20, wait=.2):
    cmd = 'fswebcam -s brightness=%d -q --no-banner --background %s' % (brightness, to_file)
    os.system(cmd)
    time.sleep(wait)
    im = cv2.imread(to_file)
    return im

def find(im, classifier=MTG_BACK_CLASSIFIER, min_size=(W,H), scale_factor=1.1, min_neighbors=1):
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    cards = classifier.detectMultiScale(gray, scaleFactor=scale_factor, 
                minNeighbors=min_neighbors, minSize=min_size, flags=cv2.CASCADE_SCALE_IMAGE)
    centers = [(x+w/2,y+h/2) for (x,y,w,h) in cards]
    return centers

