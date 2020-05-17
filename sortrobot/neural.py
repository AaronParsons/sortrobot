'''Import the saved model from training/train_cnn.ipynb (which is
installed in sortrobot/data) for classification.'''

import tensorflow as tf

MODEL_FILE = 'data/mtg_back_front_classifier_v000'
MODEL_INPUT_SIZE = (64, 48)

class Classifier:
    def __init__(self, mdl_file=MODEL_FILE):
        self.model = tf.keras.models.load_model(mdl_file)
    def classify(self, im):
        im = tf.image.resize(im, MODEL_INPUT_SIZE)
            #method=ResizeMethod.BILINEAR, preserve_aspect_ratio=False,
            #antialias=False, name=None)
        prediction = self.model(im, training=False)
        return prediction

