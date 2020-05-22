#! /usr/bin/env python

from sortrobot.neural import Classifier, OrientationClassifier
from PIL import Image
import sys, os
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-o", "--outdir", dest="outdir", default=None,
                   help="Directory to write sorted files. Default: same directory as file.")
parser.add_option("-c", "--classifier", dest="classifier", default='orient',
                   help="Classifier from sortrobot.neural to use.")
opts, args = parser.parse_args(sys.argv[1:])

classifier = {
    'orient': OrientationClassifier,
    'color': Classifier,
}[opts.classifier]()

for i,filename in enumerate(args):
    print('{}: Reading {}'.format(i, filename))
    im = Image.open(filename)
    label = classifier.classify(im)
    print('    classified as', label)
    outdir, basename = os.path.split(filename)
    if opts.outdir is not None:
        outdir = opts.outdir
    newdir = os.path.join(outdir, label)
    if not os.path.exists(newdir):
        os.mkdir(newdir)
    print('    moving to', newdir)
    os.rename(filename, os.path.join(newdir, basename))
