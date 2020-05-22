#! /usr/bin/env python

from sortrobot.mech import Robot
from sortrobot.webcam import Camera
from sortrobot.cardface import extract_titlebar
from sortrobot.ocr import titlebar_to_text
from sortrobot.web import lookup
from sortrobot.utils import random_filename
from sortrobot.neural import OrientationClassifier
import numpy as np
from PIL import Image
import sys, random, os
import json
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-o", "--outdir", dest="outdir", default='/home/pi/scans',
                  help="Directory to write sorted scans.")
parser.add_option("-f", "--field", dest="field", default='rarity',
                   help="Database field to sort by.")
parser.add_option("-c", "--crop", dest="crop", default="80,80,160,570",
      help="Comma-delimited list of xmin,ymin,xmax,ymax cropping.")
parser.add_option("-v", "--verbose", dest="verbose",
                  action='store_true', default=False,
                   help="Print verbose debug info.")
opts, args = parser.parse_args(sys.argv[1:])

directory = opts.outdir
assert os.path.exists(directory)

def echo(*args):
    if opts.verbose:
        print(*args)

DEFAULT_ORDER = 'common,uncommon rare mythic unknown'

classifier = OrientatonClassifier()
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

    def identify(filename):
        try:
            echo('    SCRIPT: using cropping:', precrop)
            title_bar = extract_titlebar(filename, precrop=precrop,
                                         verbose=opts.verbose)
        except(AssertionError):
            echo('    SCRIPT: retrying titlebar extraction w/o cropping.')
            try:
                title_bar = extract_titlebar(filename, verbose=opts.verbose)
            except(AssertionError):
                echo('    SCRIPT: Failed to find title bar.')
                return {}
        try:
            text = titlebar_to_text(title_bar, verbose=opts.verbose)
        except(AssertionError):
            from skimage.transform import rotate
            text = ''
            for ang in [-0.5, 0.5, -1,1,-2,2]:
                echo('    SCRIPT: brute force rotate {} deg'.format(ang))
                rot_title_bar = rotate(title_bar, ang)
                try:
                    text = titlebar_to_text(rot_title_bar,verbose=opts.verbose)
                    title_bar = rot_title_bar
                    break
                except(AssertionError):
                    pass
            if len(text) == 0:
                echo('    SCRIPT: brute force rotate failed.')
                return {}
        try:
            info = lookup(text, verbose=opts.verbose)
            echo('    SCRIPT: found entry for {}'.format(info['name']))
            return info
        except(ValueError):
            echo('    {} lookup failed'.format(text))
            return {}

    # Loop for sorting entire stack according to positions
    for i in range(MAXITER):
        # Get image of next card
        filebase = random_filename()
        filename = os.path.join(directory, filebase)
        print('%d scanning -> %s' % (i, filename))
        cam.rgb_to_file(filename)
        # Make sure stack is not empty
        with Image.open(filename) as im:
            orientation = classifier.classify(im)
        if orientation == 'empty':
            break
        elif orientation != 'top_front':
            label = 'unknown'
        else: # has correct orientation
            # use OCR to get database entry for card
            info = scan_and_lookup()
            if opts.field in info:
                # We had a successful lookup: save info
                infofile = filename[:len('.jpg')] + '.json'
                with open(infofile, 'wb') as f:
                    echo('    SCRIPT: storing info in {}'.format(infofile))
                    json.dump(info, f)
                label = info[opts.field]
            else:
                label = 'unknown'
        echo('      SCRIPT: classfied as %s' % (label))
        new_directory = os.path.join(directory, label)
        if not os.path.exists(new_directory):
            os.mkdir(new_directory)
        print('      moving to %s' % (new_directory))
        os.rename(filename, os.path.join(new_directory, filebase))
        go(label)
        sr.feed_card()

    # After sorting entire stack, give user opportunity to reload
    order = '' # triggers prompt for input at top of loop
