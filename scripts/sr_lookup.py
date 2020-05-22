#! /usr/bin/env python

import sys
from optparse import OptionParser
from sortrobot.cardface import extract_titlebar
from sortrobot.ocr import titlebar_to_text
from sortrobot.web import lookup

parser = OptionParser()
parser.add_option("-w", "--web", dest="web",
                  action='store_true', default=False,
                   help="Look up cards on the web.")
parser.add_option("-p", "--plot", dest="plot",
                  action='store_true', default=False,
                   help="Plot extracted title bar.")
parser.add_option("-v", "--verbose", dest="verbose",
                  action='store_true', default=False,
                   help="Print verbose debug info.")
opts, args = parser.parse_args(sys.argv[1:])

if opts.plot:
    import matplotlib.pyplot as plt

for filename in args:
    try:
        title_bar = extract_titlebar(filename, verbose=opts.verbose)
    except(AssertionError):
        print(filename, 'Failed to find title bar.')
        continue
    try:
        text = titlebar_to_text(title_bar, verbose=opts.verbose)
    except(AssertionError):
        from skimage.transform import rotate
        text = ''
        for ang in [-0.5, 0.5, -1,1,-2,2]:
            if opts.verbose:
                print('    SCRIPT: brute force rotate {} deg'.format(ang))
            rot_title_bar = rotate(title_bar, ang)
            try:
                text = titlebar_to_text(rot_title_bar,verbose=opts.verbose)
                title_bar = rot_title_bar
                break
            except(AssertionError):
                pass
        if opts.verbose and len(text) == 0:
            print('    SCRIPT: brute force rotate failed.')

    if opts.plot:
        plt.imshow(title_bar, cmap=plt.cm.gray)
        plt.gca().axis('off')
        if len(text) > 0:
            plt.title(text)
        else:
            plt.title('Failed')
        plt.show()

    if opts.web:
        try:
            info = lookup(text, verbose=opts.verbose)
            print(filename,
                info['name'],
                info['colors'],
                info['rarity'],
                info['prices']['usd'])
        except(ValueError):
            print(filename, text, '(lookup failed)')
            
    else:
        print(filename, text)
