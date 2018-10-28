from __future__ import print_function
import threading, Queue
from . import mech
from . import find

#SAVEFILE = 'training/mtg_back002.ckpl'
SAVEFILE = 'training/mtg_back_v003.ckpl'

class Robot(mech.Robot):
    def __init__(self, session, savefile=SAVEFILE, Vin=6., Vmotor=6., verbosity=1):
        mech.Robot.__init__(self, Vin=Vin, Vmotor=Vmotor, verbosity=verbosity)
        if verbosity >= 1: print('Restoring from', savefile)
        self._finder = find.FinderCNN(session, savefile)
        self._cards = Queue.Queue()
        self.filename = None
    def find(self, block=True, shift=0):
        def find_thread():
            im = self.take_pic(shift=shift)
            cards = self._finder.find(im)
            self._cards.put(cards)
        thd = threading.Thread(target=find_thread)
        thd.start()
        if block: thd.join()
        else: return thd
    def sort(self, ncards, minpos=1, pos1=mech.POS2, pos2=mech.POS1, hgt=mech.HEIGHT):
        find_thd = self.find(block=False, shift=pos2)
        for i in range(ncards):
            find_thd.join()
            cards = self._cards.get()
            if self.verbosity >= 1: print('Card positives:', cards)
            cnt = 0
            for cx0,cy0 in cards:
                dist = [(cx0-cx)**2 + (cy0-cy)**2 for cx,cy in cards]
                new_cnt = len([d for d in dist if d <= (1.5 * self._finder.half_sz)**2])
                cnt = max(cnt, new_cnt)
            #cards = find.find_from_file(filename)
            #if any([x < 100 for x,y in cards]):
            if cnt >= minpos:
                if self.verbosity >= 1: print('%d/%d' % (i+1,ncards), self.filename, ': back')
                pos = pos1
            else:
                if self.verbosity >= 1: print('%d/%d' % (i+1,ncards), self.filename, ': front')
                pos = pos2
            self.carry_card(pos, hgt=hgt)
            find_thd = self.find(block=False)
            self.home(pos=pos)
