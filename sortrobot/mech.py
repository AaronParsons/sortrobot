from __future__ import print_function
import time, numpy
import threading
from . import webcam
try:
    # installed if we are on rpi, else ImportError
    from rrb3 import RRB3 # requires AaronParsons fork
except(ImportError):
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
DN_SPEED = 0.965
UP_SPEED = 1.
LIFT_TIME = 0.33
SLIDE_LF_SPEED = 1.
SLIDE_RT_SPEED = 0.9625
SLIDE_TIME = 0.1125
SLIDE_POLY = numpy.array([1.07980235e-04,-1.45621868e-03,1.98557185e-03,5.55231344e-01,2.23568309e-01])

# DEFAULT POSITIONS
HEIGHT = 4
POS1 = 6
POS2 = 12

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
            self._driver.set_left_motor(abs(m1), direction(m1))
        if m2 is not None:
            self._driver.set_right_motor(abs(m2), direction(m2))
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
    def valve_close(self):
        '''Close the valve, which propagates vacuum to the cup.'''
        self._oc_cmd(oc1=0)
    def valve_open(self):
        '''Open the valve, which breaks the vacuum.'''
        self._oc_cmd(oc1=1)
    def pump_on(self):
        '''Turn on the pump to generate suction.'''
        self._oc_cmd(oc2=1)
    def pump_off(self):
        '''Turn on the pump to stop generating suction.'''
        self._oc_cmd(oc2=0)
    def up(self, distance, block=True):
        '''Move the robot arm up the specified distance.
        Arguments:
            distance: nominally inches of displacment, but not accurate.
            block: if True, wait until motion completes before returning,
                otherwise return a handle to the thread in charge of stopping motion.
        Returns:
            None, unless block is False, then Thread handle.'''
        dt = distance * LIFT_TIME
        if self.verbosity >= 1: print('UP:', dt)
        def up_thread():
            self._motor_cmd(m1=UP_SPEED)
            time.sleep(dt)
            self._motor_cmd(m1=0.)
        thd = threading.Thread(target=up_thread)
        thd.start()
        if block: thd.join()
        else: return thd
    def dn(self, distance, block=True):
        '''Move the robot arm down the specified distance.
        Arguments:
            distance: nominally inches of displacment, but not accurate.
            block: if True, wait until motion completes before returning,
                otherwise return a handle to the thread in charge of stopping motion.
        Returns:
            None, unless block is False, then Thread handle.'''
        dt = distance * LIFT_TIME
        if self.verbosity >= 1: print('DN:', dt)
        def dn_thread():
            self._motor_cmd(m1=-DN_SPEED)
            time.sleep(dt)
            self._motor_cmd(m1=0.)
        thd = threading.Thread(target=dn_thread)
        thd.start()
        if block: thd.join()
        else: return thd
    def lf(self, distance, block=True):
        '''Move the slide tray left the specified distance.
        Arguments:
            distance: nominally inches of displacment, but not accurate.
            block: if True, wait until motion completes before returning,
                otherwise return a handle to the thread in charge of stopping motion.
        Returns:
            None, unless block is False, then Thread handle.'''
        dt = numpy.polyval(SLIDE_POLY, distance) * SLIDE_TIME
        if self.verbosity >= 1: print('LF:', dt)
        def lf_thread():
            self._motor_cmd(m2=-SLIDE_LF_SPEED)
            time.sleep(dt)
            self._motor_cmd(m2=0)
        thd = threading.Thread(target=lf_thread)
        thd.start()
        if block: thd.join()
        else: return thd
    def rt(self, distance, block=True):
        '''Move the slide tray right the specified distance.
        Arguments:
            distance: nominally inches of displacment, but not accurate.
            block: if True, wait until motion completes before returning,
                otherwise return a handle to the thread in charge of stopping motion.
        Returns:
            None, unless block is False, then Thread handle.'''
        dt = numpy.polyval(SLIDE_POLY, distance) * SLIDE_TIME
        if self.verbosity >= 1: print('RT:', dt)
        def rt_thread():
            self._motor_cmd(m2=SLIDE_RT_SPEED)
            time.sleep(dt)
            self._motor_cmd(m2=0)
        thd = threading.Thread(target=rt_thread)
        thd.start()
        if block: thd.join()
        else: return thd
    #def accel_lf(self, dt, dV_dt=4., Vmin=.4, update=.05):
    #    V = Vmin
    #    t0 = time.time()
    #    while True:
    #        V = min(1., V + dV_dt * update)
    #        print time.time()-t0, dt, V, dt - V / dV_dt
    #        self._motor_cmd(m2=-V)
    #        time.sleep(update)
    #        if time.time() - t0 > dt - (V-Vmin) / dV_dt: break
    #    while True:
    #        V = max(Vmin, V - dV_dt * update)
    #        print time.time() - t0, dt, V
    #        self._motor_cmd(m2=-V)
    #        if V <= Vmin: break
    #        time.sleep(update)
    #    self._motor_cmd(m2=0)
    def grab(self):
        '''Turn the pump on and close the valve to grab a card.'''
        self.pump_on()
        self.valve_close()
    def release(self, dt=.5, block=False):
        '''Break the vacuum seal to drop the card.
        Arguments:
            dt: how long to release the card before reestablishing vacuum.
            block: if True, wait until motion completes before returning,
                otherwise return a handle to the thread in charge of stopping motion.
        Returns:
            None, unless block is False, then Thread handle.'''
        def release_thread():
            self.valve_open() # release pressure
            time.sleep(dt)
            self.valve_close() # stop wasting valve current
        thd = threading.Thread(target=release_thread)
        thd.start()
        if block: thd.join()
        else: return thd
    def home(self, pos=POS2, hgt=HEIGHT):
        '''Move robot arm up and slide tray all the way to the left.'''
        self.up(hgt)
        self.lf(pos + 0.25)
    def carry_card(self, pos=POS2, hgt=HEIGHT):
        '''Assuming you are HOME, pick up a card and move it to a new stack.
        Arguments:
            pos: the position to the right of the new stack.  Default POS2.
            hgt: the height of the robot arm in the up position.  Default HEIGHT.'''
        self.grab()
        self.dn(hgt)
        up_thd = self.up(hgt, block=False)
        # Shimmy to shake off cards
        self.rt(.1); self.lf(.1)
        self.rt(.1); self.lf(.1)
        self.rt(.1); self.lf(.1)
        up_thd.join()
        self.rt(pos)
        self.dn(hgt)
        self.release()
        self.pump_off()
    def move_card(self, pos=POS2, hgt=HEIGHT):
        '''Fron HOME, pick up a card, move it to a new stack, and return HOME.
        Arguments:
            pos: the position to the right of the new stack.  Default POS2.
            hgt: the height of the robot arm in the up position.  Default HEIGHT.'''
        self.carry_card(pos=pos, hgt=hgt)
        self.home(pos=pos, hgt=hgt)
    def take_pic(self, shift=POS2):
        '''Take a picture from the webcam and return the image as a numpy array.
        Arguments:
            shift: the distance to move the arm right out of the way before taking
                the pic.  Default POS2.
        Returns:
            im: the image as a numpy array.'''
        self.rt(shift)
        self.filename, im = webcam.read().items()[0]
        if self.verbosity >= 1: print('Webcam:', self.filename)
        self.lf(shift)
        return im
