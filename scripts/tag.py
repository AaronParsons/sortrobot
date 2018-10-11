#! /usr/bin/env python
import pylab as plt
import sys, PIL, numpy as np
import cPickle, os

filelist = sys.argv[1:]
labels = {os.path.basename(f): [] for f in filelist}
try:
    pickle_file = open('labels.pkl','r')
    labels.update(cPickle.load(pickle_file))
except(IOError):
    pass

cnt = 0
im = PIL.Image.open(filelist[cnt])
img_plt = plt.imshow(im)
curfile = os.path.basename(filelist[cnt])
lbl_plt = plt.plot([x for x,y in labels[curfile]], [y for x,y in labels[curfile]], 'm.')[0]

def click(event):
    global labels
    curfile = os.path.basename(filelist[cnt])
    if event.button == 1:
        x,y = int(np.around(event.xdata)), int(np.around(event.ydata))
        labels[curfile] = labels.get(curfile, []) + [(x,y)]
    elif event.button == 3:
        labels[curfile] = labels.get(curfile, [None])[:-1]
    lbl_plt.set_xdata([x for x,y in labels[curfile]])
    lbl_plt.set_ydata([y for x,y in labels[curfile]])
    plt.draw()
    print labels[curfile]

def press(event):
    global cnt
    if event.key == 'n':
        print 'Writing labels'
        f = open('labels.pkl', 'w')
        cPickle.dump(labels, f)
        f.close()
        cnt += 1
        im = PIL.Image.open(filelist[cnt])
        img_plt.set_data(im)
        curfile = os.path.basename(filelist[cnt])
        lbl_plt.set_xdata([x for x,y in labels[curfile]])
        lbl_plt.set_ydata([y for x,y in labels[curfile]])
        plt.draw()

plt.connect('button_press_event', click)
plt.connect('key_press_event', press)
plt.show()
