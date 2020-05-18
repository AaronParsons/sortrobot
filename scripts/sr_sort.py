from sortrobot.mech import Robot
from sortrobot.webcam import Camera
from sortrobot.neural import Classifier
import numpy as np
from PIL import Image
import sys, random, os

def random_filename(lim=2**13):
    hexstr = hex(random.randint(0,lim))[2:]
    hexstr = ('0' * 8 + hexstr)[-8:]
    return hexstr + '.jpg'

num = int(sys.argv[-2])
directory = sys.argv[-1]

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

sr.lf(UNIT)
curpos = 'back'

for i in range(num):
    filebase = random_filename()
    filename = os.path.join(directory, filebase)
    print('%d/%d scanning -> %s' % (i, num, filename))
    cam.rgb_to_file(filename)
    im = Image.open(filename)
    prediction = classifier.classify(im)
    r = RESULTS[np.argmax(prediction)]
    print('      classfied as %s' % (r))
    new_directory = os.path.join(directory, r)
    if not os.path.exists(new_directory):
        os.mkdir(new_directory)
    print('      moving to %s' % (new_directory))
    os.rename(filename, os.path.join(new_directory, filebase))
    if r == 'empty':
        break
    if curpos != r:
        if r == 'back':
            sr.lf(UNIT)
        elif r == 'front':
            sr.rt(UNIT)
        else: # mana
            if curpos == 'back':
                sr.rt(UNIT * 0.25)
            else:
                sr.lf(UNIT)
                sr.rt(UNIT * 0.25)
    curpos = r
    sr.feed_card(FD=0.27)

