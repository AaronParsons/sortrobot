import sortrobot.find
import tensorflow as tf
import sys
import pylab as plt
import cv2
import numpy as np

savefile = sys.argv[1]

with tf.Session() as session:
    finder = sortrobot.find.FinderCNN(session, savefile)
    for filename in sys.argv[2:]:
        print 'Reading', filename
        im = cv2.imread(filename)
        all_centers = finder.gen_centers(im.shape[:-1], step=24, xrng=(0,120), yrng=(0,200))
        all_centers = np.array(all_centers)
        centers = np.array(finder.find(im))
        im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
        plt.imshow(im)
        plt.plot(all_centers[:,0], all_centers[:,1], 'k.')
        if centers.size > 0:
            plt.plot(centers[:,0], centers[:,1], 'm.')
        plt.show()
