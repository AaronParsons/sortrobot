from sortrobot.mech import Robot
from sortrobot.webcam import Camera
import sys, random, os

def random_filename(lim=2**31):
    hexstr = hex(random.randint(0, lim))[2:]
    hexstr = ('0' * 8 + hexstr)[-8:]
    return hexstr + '.jpg'

num = int(sys.argv[-2])
directory = sys.argv[-1]

sr = Robot()
cam = Camera()

for i in range(num):
    filebase = random_filename()
    filename = os.path.join(directory, filebase)
    print('%d/%d scanning ->' % (i, num), filename)
    cam.rgb_to_file(filename)
    sr.feed_card()

