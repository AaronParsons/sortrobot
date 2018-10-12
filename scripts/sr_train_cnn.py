import sortrobot, glob, os

LABELS = '../training/labels_v001.pkl'
DATADIR = '../data/observed'
OUTFILE = 'out.ckpl'

labdict = sortrobot.labels.load(LABELS)
files = glob.glob(os.path.join(DATADIR, 'tmp*'))
sortrobot.train.train(OUTFILE, files, labdict, 'back', 2000, 100)
