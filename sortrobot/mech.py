import time
import threading

try:
    # works if we are on rpi, else ImportError on GPIO
    from .rrb3 import RRB3
except(ImportError):
    import warnings
    warnings.warn('Running without RRB3 interface')

    class RRB3:
        '''A dummy wrapper to allow testing when not on rpi.'''
        def __init__(self, *args, **kwargs):
            pass
        def set_motors(self, v1, d1, v2, d2):
            pass
        def set_oc1(self, on_off):
            pass
        def set_oc2(self, on_off):
            pass

# SPEED CONSTANTS
FD_SPEED = 0.75
BK_SPEED = 1.
SLIDE_LF_SPEED = 0.5
SLIDE_RT_SPEED = 0.5

# DEFAULT POSITIONS
POSITIONS = (0,1,2,3)
SLIDE_WIDTH = 0.55 # length s.t. width/speed = time
CARD_WIDTH = 0.16 # length s.t. width/speed = time

def direction(v):
    return int(v < 0)

class Robot:
    '''Interface for controling the mechanics of the SortRobot.'''
    def __init__(self, Vin=6., Vmotor=6., verbosity=1):
        self.verbosity = verbosity
        self._driver = RRB3(Vin,Vmotor)
        self._motor_lock = threading.Lock()
        self._oc_lock = threading.Lock()
        self._stop_event = threading.Event()
        self.stop()
        # Initialize to home position
        self._curpos = 3
        self.go(0) # resets curpos to 0, move slide full scale
    def _motor_cmd(self, m1=None, m2=None):
        '''Low-level interface for the m1/m2 motors, which are nominally
        the card feed and slide tray, respectively.  Input values are 
        scalars whose sign defines direction and whose magnitude 
        define speed.'''
        if self._stop_event.is_set(): return
        self._motor_lock.acquire()
        if m1 is not None:
            self._driver.set_right_motor(abs(m1), direction(m1))
        if m2 is not None:
            self._driver.set_left_motor(abs(m2), direction(m2))
        if self.verbosity >= 2:
            print('    MECH: motor command', m1, m2)
        self._motor_lock.release()
    def _oc_cmd(self, oc1=None, oc2=None):
        '''Low-level interface to oc1 and oc2 on/off switches (currently
        unused).  Input values are on (1) or off (0).'''
        if self._stop_event.is_set(): return
        self._oc_lock.acquire()
        if oc1 is not None:
            self._driver.set_oc1(oc1)
        if oc2 is not None:
            self._driver.set_oc2(oc2)
        self._oc_lock.release()
    def stop(self):
        '''Turn off all motors and switches.'''
        self._stop_event.set()
        # Access driver directly to supercede locks
        self._driver.set_motors(0, 0, 0, 0)
        self._driver.set_oc1(0)
        self._driver.set_oc2(0)
        # Make sure all threads have cleared out
        for thread in threading.enumerate():
            try:
                thread.join(timeout=5)
            except(RuntimeError): # Can't join own thread
                pass
        # After clearing all threads, re-enable access
        self._stop_event.clear()
    def bk(self, dt, block=True):
        '''Pull a card back the specified time length.
        Arguments:
            dt: seconds
            block: if True, wait until motion completes before returning,
                otherwise return a handle to the thread in charge of
                stopping motion.
        Returns:
            None, unless block is False, then Thread handle.'''
        if self.verbosity >= 1:
            print('    MECH: bk', dt)
        def bk_thread():
            self._motor_cmd(m1=BK_SPEED)
            time.sleep(dt)
            self._motor_cmd(m1=0.)
        thd = threading.Thread(target=bk_thread)
        thd.start()
        if block: thd.join()
        else: return thd
    def fd(self, dt, block=True):
        '''Push a card forward the specified time length.
        Arguments:
            dt: seconds
            block: if True, wait until motion completes before returning,
                otherwise return a handle to the thread in charge of
                stopping motion.
        Returns:
            None, unless block is False, then Thread handle.'''
        if self.verbosity >= 1:
            print('    MECH: fd', dt)
        def fd_thread():
            self._motor_cmd(m1=-FD_SPEED)
            time.sleep(dt)
            self._motor_cmd(m1=0.)
        thd = threading.Thread(target=fd_thread)
        thd.start()
        if block: thd.join()
        else: return thd
    def lf(self, dt, block=True):
        '''Move the slide tray left the specified time length.
        Arguments:
            dt: seconds
            block: if True, wait until motion completes before returning,
                otherwise return a handle to the thread in charge of
                stopping motion.
        Returns:
            None, unless block is False, then Thread handle.'''
        if self.verbosity >= 1:
            print('    MECH: lf', dt)
        def lf_thread():
            self._motor_cmd(m2=-SLIDE_LF_SPEED)
            time.sleep(dt)
            self._motor_cmd(m2=0)
        thd = threading.Thread(target=lf_thread)
        thd.start()
        if block: thd.join()
        else: return thd
    def rt(self, dt, block=True):
        '''Move the slide tray right the specified time length.
        Arguments:
            dt: seconds
            block: if True, wait until motion completes before returning,
                otherwise return a handle to the thread in charge of
                stopping motion.
        Returns:
            None, unless block is False, then Thread handle.'''
        if self.verbosity >= 1:
            print('    MECH: rt', dt)
        def rt_thread():
            self._motor_cmd(m2=SLIDE_RT_SPEED)
            time.sleep(dt)
            self._motor_cmd(m2=0)
        thd = threading.Thread(target=rt_thread)
        thd.start()
        if block: thd.join()
        else: return thd
    def go(self, pos):
        assert pos in POSITIONS
        if pos == self._curpos:
            return
        if pos == 0: # far left
            self.lf(SLIDE_WIDTH / SLIDE_LF_SPEED * \
                    self._curpos / len(POSITIONS) + 0.1)
        elif pos == 1: # next to left
            self.go(0)
            self.rt(SLIDE_WIDTH / SLIDE_RT_SPEED * 0.3)
        elif pos == 2: # next to right
            self.go(3)
            self.lf(SLIDE_WIDTH / SLIDE_RT_SPEED * 0.33) # little extra
        elif pos == 3: # far right
            self.rt(SLIDE_WIDTH / SLIDE_RT_SPEED * \
                    (3 - self._curpos) / len(POSITIONS) + 0.1)
        self._curpos = pos
    def feed_card(self, FD=CARD_WIDTH/FD_SPEED,
            BK=CARD_WIDTH/BK_SPEED/1.8):
        '''Push a card off the stack and pull the next one back in.
        Arguments:
            FD: how much to feed forward
            BK: how much to pull back'''
        self.fd(FD)
        self.bk(BK)
