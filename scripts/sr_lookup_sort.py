#! /usr/bin/env python

from sortrobot.mech import Robot
from sortrobot.webcam import Camera
from sortrobot.utils import random_filename
from sortrobot.neural import OrientationClassifier
from sortrobot.labels import identify, label_color, label_type, \
                              label_rarity
from PIL import Image
import sys, os
import json
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-o", "--outdir", dest="outdir", default='/home/pi/scans',
                  help="Directory to write sorted scans.")
parser.add_option("-f", "--field", dest="field", default='type',
                   help="Database field to sort by.")
parser.add_option("-c", "--crop", dest="crop", default="80,80,160,570",
      help="Comma-delimited list of xmin,ymin,xmax,ymax cropping.")
parser.add_option("-v", "--verbose", dest="verbose",
                  action='store_true', default=False,
                   help="Print verbose debug info.")
opts, args = parser.parse_args(sys.argv[1:])

directory = opts.outdir
assert os.path.exists(directory)

precrop = list(int(x) for x in opts.crop.split(','))
get_label = {
    'color': label_color,
    'type': label_type,
    'rarity': label_rarity,
}[opts.field]

def echo(*args):
    if opts.verbose:
        print(*args)

DEFAULT_ORDER = {
    'color': 'G U B unknown,none,multi,W,R',
    'type': 'creature spell land other,unknown',
    'rarity':'common uncommon rare,mythic unknown',
}[opts.field]

classifier = OrientationClassifier()
order = ' '.join(args)

sr = Robot()
cam = Camera()

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

    def go(pos):
        if type(pos) is str:
            try:
                pos = POSITIONS[label]
            except(KeyError):
                print('    label %s has no position! Choosing 0.' % label)
                pos = 0
        sr.go(pos)

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
            new_directory = os.path.join(directory, 'empty')
            if not os.path.exists(new_directory):
                os.mkdir(new_directory)
            print('      moving to %s' % (new_directory))
            os.rename(filename, os.path.join(new_directory, filebase))
            break
        elif orientation != 'top_front':
            label = 'unknown'
        else: # has correct orientation
            # use OCR to get database entry for card
            info = identify(filename, precrop=precrop,
                            verbose=opts.verbose)
            if len(info) > 0:
                # We had a successful lookup: save info
                infofile = filename[:-len('.jpg')] + '.json'
                with open(infofile, 'w') as f:
                    echo('    SCRIPT: storing info in {}'.format(infofile))
                    json.dump(info, f)
            label = get_label(info)
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
