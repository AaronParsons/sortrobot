import sortrobot
import tensorflow as tf
import sys
import pylab as plt
import cv2
import numpy as np
from sortrobot.neural import y_conv, x, keep_prob

HALF_SZ = sortrobot.neural.HALF_SZ
STEP = HALF_SZ/2
saver = tf.train.Saver()
savefile = sys.argv[1]

with tf.Session() as session:
    saver.restore(session, savefile)
    for filename in sys.argv[2:]:
        print 'Reading', filename
        im = cv2.imread(filename)
        input_x = []
        centers = []
        for cy in range(HALF_SZ, im.shape[0] - HALF_SZ, STEP):
            for cx in range(HALF_SZ, im.shape[1] - HALF_SZ, STEP):
                clip = im[cy-HALF_SZ:cy+HALF_SZ,cx-HALF_SZ:cx+HALF_SZ]
                input_x.append(clip)
                centers.append((cx,cy))
        input_x = np.array(input_x)
        k = session.run([tf.nn.softmax(y_conv)], feed_dict={x:input_x , keep_prob: 1.})

        plt.imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
        for (cx,cy),is_other in zip(centers, np.argmax(np.array(k)[0], 1)):
            if is_other: plt.plot(cx, cy, 'w.')
            else: plt.plot(cx, cy, 'm.')
        plt.show()
