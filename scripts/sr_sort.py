import sortrobot
import tensorflow as tf
import sys
        
savefile = sys.argv[1]
ncards = int(sys.argv[2])

with tf.Session() as session:
    sr = sortrobot.sortrobot.SortRobot(session, savefile)
    sr.sort(ncards)
    sr.stop()
