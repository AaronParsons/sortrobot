'''Import the saved model from training/train_cnn.ipynb (which is
installed in sortrobot/data) for classification.'''

import tensorflow as tf
import numpy as np
import os

# see https://medium.com/@JeansPantRushi/fix-for-tensorflow-v2-failed-to-get-convolution-algorithm-b367a088b56e
physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)

directory, _ = os.path.split(__file__)
MODEL_FILE = directory + '/data/mtg_back_front_classifier_v004'
MODEL_INPUT_SIZE = (48*2, 64*2)

RESULTS = {
    0: 'back',
    1: 'black',
    2: 'blue',
    3: 'empty',
    4: 'green',
    5: 'mana',
    6: 'other',
    7: 'red',
    8: 'white',
}

class Classifier:
    def __init__(self, mdl_file=MODEL_FILE, input_size=MODEL_INPUT_SIZE):
        mdl = tf.keras.models.load_model(mdl_file)
        #self.model = mdl # for binary classifiers like v001
        self.model = tf.keras.Sequential([mdl, tf.keras.layers.Softmax()])
        self.input_size = input_size
    def classify(self, im):
        im = np.array(im).astype(np.float32) / 255
        im = tf.image.resize(im, self.input_size)
            #method=ResizeMethod.BILINEAR, preserve_aspect_ratio=False,
            #antialias=False, name=None)
        im = np.expand_dims(im, axis=0)
        prediction = self.model.predict(im)
        return RESULTS[np.argmax(np.around(prediction[0]))]

