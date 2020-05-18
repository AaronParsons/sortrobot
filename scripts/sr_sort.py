from sortrobot.mech import Robot
from sortrobot.webcam import Camera
from sortrobot.neural import Classifier
from sortrobot.utils import random_filename
import numpy as np
from PIL import Image
import sys, random, os

DEFAULT_ORDER = 'black,blue,green mana back red,white,other'

directory = sys.argv[1]
assert os.path.exists(directory)

order = ' '.join(sys.argv[2:])

sr = Robot()
cam = Camera()
classifier = Classifier()

UNIT = 1.1
MAXITER = 500

while True:
    if len(order.split()) != 4:
        order = input('Enter a valid order [DEFAULT %s]: ' % DEFAULT_ORDER)
        order = order.strip()
        if len(order) == 0:
            order = DEFAULT_ORDER
        if input('Confirm order "%s" [Y/n]? ' % order).strip().lower() == 'n':
            continue
        print('Using order:', order)
    DEFAULT_ORDER = order # save for next time
    POSITIONS = {}
    for pos,arg in enumerate(order.split()):
        for label in arg.split(','):
            POSITIONS[label] = pos


    # Start at home = left = position 0
    sr.lf(UNIT)
    curpos = 0

    def go(pos):
        global curpos
        if type(pos) is str:
            try:
                pos = POSITIONS[label]
            except(KeyError):
                print('    label %s has no position! Choosing 0.' % label)
                pos = 0
        if pos == curpos:
            return
        if pos == 0: # far left
            sr.lf(UNIT)
        elif pos == 1: # next to left
            go(0)
            sr.rt(0.3 * UNIT)
        elif pos == 2: # next to right
            go(3)
            sr.lf(0.3 * UNIT)
        elif pos == 3: # far right
            sr.rt(UNIT)
        else:
            raise ValueError('Invalid position %s' % pos)
        curpos = pos

    for i in range(MAXITER):
        filebase = random_filename()
        filename = os.path.join(directory, filebase)
        print('%d scanning -> %s' % (i, filename))
        cam.rgb_to_file(filename)
        im = Image.open(filename)
        label = classifier.classify(im)
        print('      classfied as %s' % (label))
        new_directory = os.path.join(directory, label)
        if not os.path.exists(new_directory):
            os.mkdir(new_directory)
        print('      moving to %s' % (new_directory))
        os.rename(filename, os.path.join(new_directory, filebase))
        if label == 'empty':
            break
        go(label)
        sr.feed_card()
    order = '' # triggers prompt for input at top of loop
