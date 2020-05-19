#! /usr/bin/env python

import tensorflow as tf; tf.logging.set_verbosity(tf.logging.ERROR)
from sortrobot.sort import Robot
import IPython
        
with tf.Session() as session:
    sr = Robot(session)
    IPython.embed()
