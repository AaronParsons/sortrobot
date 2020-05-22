#! /usr/bin/env python

from sortrobot.neural import Classifier, OrientationClassifier
from PIL import Image
import sys
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-c", "--classifier", dest="classifier", default='orient',
                   help="Classifier from sortrobot.neural to use.")
parser.add_option("-i", "--interpret", dest="interpret",
                  action='store_true', default=False,
                   help="Interpret output of neural net.")
opts, args = parser.parse_args(sys.argv[1:])

classifier = {
    'orient': OrientationClassifier,
    'color': Classifier,
}[opts.classifier]()

for filename in args:
    im = Image.open(filename)
    prediction = classifier.classify(im, interpret=opts.interpret)
    print(filename, '->', prediction)
