#! /usr/bin/env python
import pylab as plt
import sys, cv2, numpy as np
import cPickle, os

filelist = sys.argv[1:]
labdict = {os.path.basename(f): [] for f in filelist}
try:
    pickle_file = open('labels.pkl','r')
    labdict.update(cPickle.load(pickle_file))
except(IOError):
    pass

labels = set([label for lablist in labdict.values() for x,y,label in lablist])
labels = {label: cnt for cnt, label in enumerate(labels)}
filecnt = 0
im = cv2.imread(filelist[filecnt])
img_plt = plt.imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
curfile = os.path.basename(filelist[filecnt])

colors = [color + symbol for color in 'mgcbw' for symbol in 'o^vh']
lab_plots = {}

def update_plot(plts, label):
    global lab_plots
    data = np.array([(x,y) for x,y,L in labdict[curfile] if L == label])
    if data.size == 0:
        data = np.empty((0,2))
    print label, data
    if plts.has_key(label):
        lplt = lab_plots[label]
        lplt.set_xdata(data[:,0])
        lplt.set_ydata(data[:,1])
    else:
        labels[label] = len(labels)
        color = colors[labels[label] % len(colors)]
        lab_plots[label] = plt.plot(data[:,0], data[:,1], color)[0]
    return

for label in labels.keys():
    update_plot(lab_plots, label)

def get_cur_label():
    print 'Current labels:'
    print ', '.join(labels)
    cur_label = raw_input('Enter new label: ')
    print 'New current label:', cur_label
    return cur_label

cur_label = get_cur_label()

def click(event):
    global labdict
    curfile = os.path.basename(filelist[filecnt])
    if event.button == 1:
        x,y = int(np.around(event.xdata)), int(np.around(event.ydata))
        labdict[curfile] = labdict.get(curfile, []) + [(x,y,cur_label)]
    elif event.button == 3:
        labdict[curfile] = labdict.get(curfile, [None])[:-1]
    update_plot(lab_plots, cur_label)
    plt.draw()
    print labdict[curfile]

def press(event):
    global filecnt
    global cur_label
    global curfile
    if event.key == 'n':
        print 'Writing labels'
        f = open('labels.pkl', 'w')
        cPickle.dump(labdict, f)
        f.close()
        filecnt += 1
        im = cv2.imread(filelist[filecnt])
        img_plt.set_data(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
        plt.draw()
        curfile = os.path.basename(filelist[filecnt])
        for label in labels.keys():
            update_plot(lab_plots, label)
        plt.draw()
    if event.key == 'y':
        cur_label = get_cur_label()
        if cur_label not in labels:
            labels[cur_label] = len(labels)

plt.connect('button_press_event', click)
plt.connect('key_press_event', press)
plt.show()
