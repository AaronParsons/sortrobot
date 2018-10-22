from __future__ import print_function
import time, tempfile
import find
import threading, Queue
import mech
import cv2

SAVEFILE = 'training/mtg_back002.ckpl'

class Robot(mech.Robot):
    def __init__(self, session, savefile=SAVEFILE, Vin=6., Vmotor=6., verbose=False):
        mech.Robot.__init__(self, Vin=Vin, Vmotor=Vmotor, verbose=verbose)
        self._finder = find.FinderCNN(session, savefile)
        self._cards = Queue.Queue()
        self.filename = None
    def find(self, block=True):
        _, self.filename = tempfile.mkstemp()
        im = find.read_webcam(self.filename)
        def find_thread():
            cards = self._finder.find(im)
            self._cards.put(cards)
        thd = threading.Thread(target=find_thread)
        thd.start()
        if block: thd.join()
        else: return thd
    def sort(self, ncards, pos1=mech.POS2, pos2=mech.POS1, hgt=mech.HEIGHT):
        self.rt(pos2)
        find_thd = self.find(block=False)
        self.lf(pos2)
        for i in range(ncards):
            find_thd.join()
            cards = self._cards.get()
            print(cards)
            cnt = 0
            for cx0,cy0 in cards:
                dist = [(cx0-cx)**2 + (cy0-cy)**2 for cx,cy in cards]
                new_cnt = len([d for d in dist if d <= (1.5 * self._finder.half_sz)**2])
                cnt = max(cnt, new_cnt)
            print(cnt)
            #cards = find.find_from_file(filename)
            #if any([x < 100 for x,y in cards]):
            if cnt >= 3:
                print('%d/%d' % (i+1,ncards), self.filename, ': back')
                pos = pos1
            else:
                print('%d/%d' % (i+1,ncards), self.filename, ': front')
                pos = pos2
            self.carry_card(pos, hgt=hgt)
            find_thd = self.find(block=False)
            self.home(pos=pos)
