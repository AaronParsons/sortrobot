from sortrobot.mech import Robot
from sortrobot.webcam import Camera
from sortrobot.neural import Classifier
from sortrobot.utils import random_filename
import numpy as np
from PIL import Image
import sys, random, os

directory = sys.argv[1]
assert os.path.exists(directory)

order = sys.argv[2:]
if len(order) != 3:
    print('Using default order: [front, back, mana]')
    order = ['front', 'back', 'mana']
POSITIONS = dict(zip(order, range(len(order))))

sr = Robot()
cam = Camera()
classifier = Classifier()

RESULTS = {
    0: 'back',
    1: 'empty',
    2: 'front',
    3: 'mana',
}

UNIT = 1.1
MAXITER = 500

sr.lf(UNIT)
curpos = 0

def go(label):
    global curpos
    pos = POSITIONS[label]
    if pos == curpos:
        return
    if pos == 0: # far left
        sr.lf(UNIT)
    elif pos == 2: # far right
        sr.rt(UNIT)
    else:
        if curpos == 0:
            sr.rt(0.4 * UNIT)
        else:
            sr.lf(UNIT)
            sr.rt(0.4 * UNIT)
    curpos = pos

for i in range(MAXITER):
    filebase = random_filename()
    filename = os.path.join(directory, filebase)
    print('%d scanning -> %s' % (i, filename))
    cam.rgb_to_file(filename)
    im = Image.open(filename)
    prediction = classifier.classify(im)
    label = RESULTS[np.argmax(prediction)]
    print('      classfied as %s' % (label))
    new_directory = os.path.join(directory, label)
    if not os.path.exists(new_directory):
        os.mkdir(new_directory)
    print('      moving to %s' % (new_directory))
    os.rename(filename, os.path.join(new_directory, filebase))
    if r == 'empty':
        break
    go(label)
    sr.feed_card()

