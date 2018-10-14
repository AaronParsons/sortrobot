import sortrobot
import tensorflow as tf
import sys
import IPython
        
savefile = sys.argv[-1]

with tf.Session() as session:
    sr = sortrobot.sortrobot.SortRobot(session, savefile)
    IPython.embed()
