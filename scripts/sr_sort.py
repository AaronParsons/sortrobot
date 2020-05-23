#! /usr/bin/env python

from sortrobot.mech import Robot
from sortrobot.webcam import Camera
from sortrobot.neural import Classifier, OrientationClassifier
from sortrobot.utils import random_filename
import numpy as np
from PIL import Image
import sys, random, os
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-o", "--outdir", dest="outdir", default='/home/pi/scans',
                  help="Directory to write sorted scans.")
parser.add_option("-c", "--classifier", dest="classifier", default='orient',
                   help="Classifier from sortrobot.neural to use.")
opts, args = parser.parse_args(sys.argv[1:])

directory = opts.outdir
assert os.path.exists(directory)
classifier = {
    'orient': OrientationClassifier,
    'color': Classifier,
}[opts.classifier]()


#DEFAULT_ORDER = 'black,blue,green mana back red,white,other'
DEFAULT_ORDER = 'top_front top_back bot_back bot_front'

order = ' '.join(args)

sr = Robot()
cam = Camera()

UNIT = 1.1
MAXITER = 500

while True:
    if len(order.split()) != 4:
        order = input('Enter a valid order [DEFAULT %s]: ' % DEFAULT_ORDER)
        order = order.strip()
        if len(order) == 0:
            order = DEFAULT_ORDER
        if input('Confirm order "%s" [Y/n]? ' % order).strip().lower() == 'n':
            order = ''
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
