import tensorflow as tf; tf.logging.set_verbosity(tf.logging.ERROR)
from sortrobot.sort import Robot
import sys
        
ncards = int(sys.argv[2])

with tf.Session() as session:
    sr = Robot(session)
    sr.sort(ncards)
    sr.stop()
