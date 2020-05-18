from sortrobot.mech import Robot
from sortrobot.webcam import Camera
from sortrobot.utils import random_filename
import sys, random, os

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

