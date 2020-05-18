from __future__ import print_function
import time, numpy
import threading
#from . import webcam
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
FD_SPEED = 0.5
BK_SPEED = 1.
SLIDE_LF_SPEED = 0.5
SLIDE_RT_SPEED = 0.5 # 0.9625

# DEFAULT POSITIONS
POS1 = 1
POS2 = 1

def direction(v):
    return int(v < 0)

class Robot:
    '''Interface for controling the mechanical and webcam functions of the SortRobot.'''
    def __init__(self, Vin=6., Vmotor=6., verbosity=1):
        self.verbosity = verbosity
        self._driver = RRB3(Vin,Vmotor)
        self._motor_lock = threading.Lock()
        self._oc_lock = threading.Lock()
        self._stop_event = threading.Event()
        self.stop()
    def _motor_cmd(self, m1=None, m2=None):
        '''Low-level interface for the m1/m2 motors, which are nominally the 
        arm and slide tray, respectively.  Input values are scalars whose sign
        defines direction and whose magnitude define speed.'''
        if self._stop_event.is_set(): return
        self._motor_lock.acquire()
        if m1 is not None:
            self._driver.set_right_motor(abs(m1), direction(m1))
        if m2 is not None:
            self._driver.set_left_motor(abs(m2), direction(m2))
        if self.verbosity >= 2: print('MOTOR CMD:', m1, m2)
        self._motor_lock.release()
    def _oc_cmd(self, oc1=None, oc2=None):
        '''Low-level interface to oc1 and oc2 on/off switches, which are
        nominally connected to the valve and pump of the suction cup,
        respectively.  Input values are on (1) or off (0).'''
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
        '''Pull a card back the specified distance.
        Arguments:
            distance: nominally inches of displacment, but not accurate.
            block: if True, wait until motion completes before returning,
                otherwise return a handle to the thread in charge of stopping motion.
        Returns:
            None, unless block is False, then Thread handle.'''
        if self.verbosity >= 1: print('BK:', dt)
        def bk_thread():
            self._motor_cmd(m1=BK_SPEED)
            time.sleep(dt)
            self._motor_cmd(m1=0.)
        thd = threading.Thread(target=bk_thread)
        thd.start()
        if block: thd.join()
        else: return thd
    def fd(self, dt, block=True):
        '''Push a card forward the specified distance.
        Arguments:
            distance: nominally inches of displacment, but not accurate.
            block: if True, wait until motion completes before returning,
                otherwise return a handle to the thread in charge of stopping motion.
        Returns:
            None, unless block is False, then Thread handle.'''
        if self.verbosity >= 1: print('FD:', dt)
        def fd_thread():
            self._motor_cmd(m1=-FD_SPEED)
            time.sleep(dt)
            self._motor_cmd(m1=0.)
        thd = threading.Thread(target=fd_thread)
        thd.start()
        if block: thd.join()
        else: return thd
    def lf(self, dt, block=True):
        '''Move the slide tray left the specified distance.
        Arguments:
            distance: nominally inches of displacment, but not accurate.
            block: if True, wait until motion completes before returning,
                otherwise return a handle to the thread in charge of stopping motion.
        Returns:
            None, unless block is False, then Thread handle.'''
        if self.verbosity >= 1: print('LF:', dt)
        def lf_thread():
            self._motor_cmd(m2=-SLIDE_LF_SPEED)
            time.sleep(dt)
            self._motor_cmd(m2=0)
        thd = threading.Thread(target=lf_thread)
        thd.start()
        if block: thd.join()
        else: return thd
    def rt(self, dt, block=True):
        '''Move the slide tray right the specified distance.
        Arguments:
            distance: nominally inches of displacment, but not accurate.
            block: if True, wait until motion completes before returning,
                otherwise return a handle to the thread in charge of stopping motion.
        Returns:
            None, unless block is False, then Thread handle.'''
        if self.verbosity >= 1: print('RT:', dt)
        def rt_thread():
            self._motor_cmd(m2=SLIDE_RT_SPEED)
            time.sleep(dt)
            self._motor_cmd(m2=0)
        thd = threading.Thread(target=rt_thread)
        thd.start()
        if block: thd.join()
        else: return thd
    def home(self, pos=POS2):
        '''Move slide tray all the way to the left.'''
        self.lf(pos + 0.25)
    def feed_card(self, FD=0.25, BK=0.1):
        '''Push a card off the stack and pull the next one back in.
        Arguments:
            FD: how much to feed forward
            BK: how much to pull back'''
        self.fd(FD)
        self.bk(BK)
