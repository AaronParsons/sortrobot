import sys
from sortrobot.neural import Classifier
from PIL import Image

c = Classifier()

for filename in sys.argv[1:]:
    im = Image.open(filename)
    prediction = c.classify(im)
    print(filename, prediction)

