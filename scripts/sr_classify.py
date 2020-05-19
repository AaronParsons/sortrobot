#! /usr/bin/env python

import sys
from sortrobot.neural import OrientationClassifier
from PIL import Image

c = OrientationClassifier()

for filename in sys.argv[1:]:
    im = Image.open(filename)
    prediction = c.classify(im, interpret=True)
    print(filename, '->', prediction)
