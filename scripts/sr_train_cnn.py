import sortrobot.labels, sortrobot.train, glob, os
import sys

LABELS = '../training/labels_v002.pkl'
DATADIR = '../data/observed'
OUTFILE = 'out.ckpl'

labdict = sortrobot.labels.load(LABELS)
files = glob.glob(os.path.join(DATADIR, 'tmp*'))
sortrobot.train.train(OUTFILE, files, labdict, 'back', 2000, 100)
