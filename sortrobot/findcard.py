import cv2, imutils, os, time
import neural
import tensorflow as tf
import numpy as np

CASCADE_MTG_BACK = 'data/cascades/cascade_mtg_back003.xml'
W,H = 48,36

MTG_BACK_CLASSIFIER = cv2.CascadeClassifier(CASCADE_MTG_BACK)

def webcam_to_file(to_file, brightness=20):
    cmd = 'fswebcam -s brightness=%d -q --no-banner --background %s' % (brightness, to_file)
    os.system(cmd)

def find_from_file(filename, classifier=MTG_BACK_CLASSIFIER, min_size=(W,H), scale_factor=1.1, min_neighbors=1):
    im = cv2.imread(filename)
    return find(im, classifier=classifier, min_size=min_size, scale_factor=scale_factor, min_neighbors=min_neighbors)

def read_webcam(to_file, brightness=20, wait=.2):
    webcam_to_file(to_file, brightness=brightness)
    time.sleep(wait)
    im = cv2.imread(to_file)
    return im

def find(im, classifier=MTG_BACK_CLASSIFIER, min_size=(W,H), scale_factor=1.1, min_neighbors=1):
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    cards = classifier.detectMultiScale(gray, scaleFactor=scale_factor, 
                minNeighbors=min_neighbors, minSize=min_size, flags=cv2.CASCADE_SCALE_IMAGE)
    centers = [(x+w/2,y+h/2) for (x,y,w,h) in cards]
    return centers

class FinderCNN:
    def __init__(self, session, savefile):
        saver = tf.train.Saver()
        saver.restore(session, savefile)
        self.session = session
        self.half_sz = neural.HALF_SZ
        self.x = neural.x
        self.y = neural.y_conv
        self.keep_prob = neural.keep_prob
    def _run(self, x_in):
        k = self.session.run([tf.nn.softmax(self.y)], feed_dict={self.x:x_in, self.keep_prob:1.})
        has_label = np.argmax(np.array(k)[0], 1) == 0
        return has_label
    def gen_centers(self, shape, step, xrng=None, yrng=None):
        assert len(shape) == 2
        if xrng is None: xrng = (0, shape[1])
        if yrng is None: yrng = (0, shape[0])
        xmin = max(xrng[0], self.half_sz)
        xmax = min(xrng[1], shape[1] - self.half_sz + 1)
        ymin = max(yrng[0], self.half_sz)
        ymax = min(yrng[1], shape[0] - self.half_sz + 1)
        centers = [(cx,cy) for cy in range(ymin, ymax, step) for cx in range(xmin, xmax, step)]
        return centers
    def get_xin(self, im, centers):
        x_in = np.array([im[cy-self.half_sz:cy+self.half_sz,cx-self.half_sz:cx+self.half_sz] for cx,cy in centers])
        return x_in.astype(np.float) / 255
    def find(self, im, xrng=(0,120), yrng=(0,200), step=24):
        centers = self.gen_centers(im.shape[:-1], step, xrng=xrng, yrng=yrng)
        x_in = self.get_xin(im, centers)
        has_label = self._run(x_in)
        return [c for c,h in zip(centers, has_label) if h]
        
