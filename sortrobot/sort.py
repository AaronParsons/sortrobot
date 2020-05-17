from __future__ import print_function
import threading, Queue
from . import mech
from . import find

#SAVEFILE = 'training/mtg_back002.ckpl'
SAVEFILE = 'training/mtg_back_v004.ckpl'

class Robot(mech.Robot):
    '''Interface for controlling the SortRobot, including using a Finder to decide whether
    cards match.  Adds sorting capability.'''
    def __init__(self, session, savefile=SAVEFILE, Vin=6., Vmotor=6., verbosity=1):
        mech.Robot.__init__(self, Vin=Vin, Vmotor=Vmotor, verbosity=verbosity)
        if verbosity >= 1: print('Restoring from', savefile)
        self._finder = find.FinderCNN(session, savefile)
        self._cards = Queue.Queue()
        self.filename = None
    def find(self, block=True, shift=0):
        '''Take a picture and use the Finder provided on init to determine where matching
        cards are within the image.  Results are stored in self._cards.
        Arguments:
            block: if True, wait until motion completes before returning,
                otherwise return a handle to the thread in charge of stopping motion.
            shift: the distance to move the arm right out of the way before taking
                the pic.  Default POS2.
        Returns:
            None, unless block is False, then Thread handle.'''
        im = self.take_pic(shift=shift)
        def find_thread():
            im = self.take_pic(shift=shift)
            cards = self._finder.find(im)
            self._cards.put(cards)
        thd = threading.Thread(target=find_thread)
        thd.start()
        if block: thd.join()
        else: return thd
    def sort(self, ncards, minpos=1, pos1=mech.POS2, pos2=mech.POS1):
        '''Sort cards into two stacks depending on whether they match or not.
        Arguments:
            ncards: the number of cards to sort.
            minpos: the minimum number of positive detections needed to be regarded as a match.
            pos1: the position to the first (non-matching) stack.  Default mech.POS2.
            pos2: the position to the second (matching) stack.  Default mech.POS1. '''
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
            find_thd = self.find(block=False)
            self.home(pos=pos)
