from sortrobot.sort import Robot
from sortrobot.webcam import Camera
from sortrobot.neural import Classifier
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
    1: 'front',
}

for i in range(num):
    filebase = random_filename()
    filename = os.path.join(directory, filebase)
    print('%d/%d scanning -> %s' % (i, num, filename))
    cam.rgb_to_file(filename)
    im = Image.open(filename)
    prediction = c.classify(im)
    r = RESULTS[int(prediction[0])]
    print('%d/%d classfied as %s' % (r))
    new_directory = os.path.join(directory, r)
    if not os.path.exists(new_directory):
        os.mkdir(new_directory)
    print('%d/%d moving to %s' % (new_directory))
    os.rename(filename, os.path.join(new_directory, filebase))
    if r == 'back':
        sr.lf(9)
    else:
        sr.rt(9)
    sr.feed_card()

