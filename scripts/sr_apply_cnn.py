import sortrobot
import sys
import pylab as plt
import cv2
import numpy as np

savefile = sys.argv[1]

with sortrobot.tensorflow.Session() as session:
    finder = sortrobot.findcard.FinderCNN(session, savefile)
    for filename in sys.argv[2:]:
        print 'Reading', filename
        im = cv2.imread(filename)
        centers = np.array(finder.find(im))
        im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
        plt.imshow(im)
        if centers.size > 0:
            plt.plot(centers[:,0], centers[:,1], 'm.')
        plt.show()
