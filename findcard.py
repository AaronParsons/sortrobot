import cv2, imutils

CASCADE_MTG_BACK = 'data/cascades/cascade_mtg_back.xml'
W,H = 48,36

MTG_BACK_CLASSIFIER = cv2.CascadeClassifier(CASCADE_MTG_BACK)

def find(filename, classifier=MTG_BACK_CLASSIFIER, min_size=(W,H), scale_factor=1.1, min_neighbors=1):
    im = cv2.imread(filename)
    im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    cards = classifier.detectMultiScale(im, scaleFactor=scale_factor, 
                minNeighbors=min_neighbors, minSize=min_size, flags=cv2.CASCADE_SCALE_IMAGE)
    centers = [(x+w/2,y+h/2) for (x,y,w,h) in cards]
    return centers

