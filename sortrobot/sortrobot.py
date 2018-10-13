from __future__ import print_function
import time, numpy, os, tempfile
import findcard
try:
    from rrb3 import RRB3 # installed if we are on rpi, else ImportError
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

#DN_SPEED = 0.5
#UP_SPEED = 0.7625
DN_SPEED = 0.66
UP_SPEED = 1.
LIFT_TIME = 0.0016666 * 300
SLIDE_LF_SPEED = 1.
SLIDE_RT_SPEED = 0.9625
SLIDE_TIME = .1125
SLIDE_POLY = numpy.array([1.07980235e-04,-1.45621868e-03,1.98557185e-03,5.55231344e-01,2.23568309e-01])

def direction(v):
    return int(v < 0)

class SortRobot:
    def __init__(self, session, savefile, Vin=6., Vmotor=6., verbose=False):
        self.verbose = verbose
        self._driver = RRB3(Vin,Vmotor)
        self._finder = findcard.FinderCNN(session, savefile)
        self.stop()
    def _send_cmd(self, m1=None, m2=None):
        if m1 is not None:
            self._m1 = m1
        if m2 is not None:
            self._m2 = m2
        self._driver.set_motors(abs(self._m1), direction(self._m1), abs(self._m2), direction(self._m2))
    def stop(self):
        self._send_cmd(0.,0.)
        self.pump_off()
        self.valve_close()
    def up(self, degrees):
        dt = degrees * LIFT_TIME
        if self.verbose: print('UP:', dt)
        self._send_cmd(m1=UP_SPEED)
        time.sleep(dt)
        self._send_cmd(m1=0.)
    def dn(self, degrees):
        dt = degrees * LIFT_TIME
        if self.verbose: print('DN:', dt)
        self._send_cmd(m1=-DN_SPEED)
        time.sleep(dt)
        self._send_cmd(m1=0.)
    def lf(self, inches):
        dt = numpy.polyval(SLIDE_POLY, inches) * SLIDE_TIME
        if self.verbose: print('LF:', dt)
        self._send_cmd(m2=-SLIDE_LF_SPEED)
        time.sleep(dt)
        self._send_cmd(m2=0)
    def rt(self, inches):
        dt = numpy.polyval(SLIDE_POLY, inches) * SLIDE_TIME
        if self.verbose: print('RT:', dt)
        self._send_cmd(m2=SLIDE_RT_SPEED)
        time.sleep(dt)
        self._send_cmd(m2=0)
    #def accel_lf(self, dt, dV_dt=4., Vmin=.4, update=.05):
    #    V = Vmin
    #    t0 = time.time()
    #    while True:
    #        V = min(1., V + dV_dt * update)
    #        print time.time()-t0, dt, V, dt - V / dV_dt
    #        self._send_cmd(m2=-V)
    #        time.sleep(update)
    #        if time.time() - t0 > dt - (V-Vmin) / dV_dt: break
    #    while True:
    #        V = max(Vmin, V - dV_dt * update)
    #        print time.time() - t0, dt, V
    #        self._send_cmd(m2=-V)
    #        if V <= Vmin: break
    #        time.sleep(update)
    #    self._send_cmd(m2=0)
    def valve_close(self):
        self._driver.set_oc1(0)
    def valve_open(self):
        self._driver.set_oc1(1)
    def pump_on(self):
        self._driver.set_oc2(1)
    def pump_off(self):
        self._driver.set_oc2(0)
    def grab(self):
        self.pump_on()
        self.valve_close()
    def release(self, dt=.1):
        self.valve_open() # release pressure
        time.sleep(dt)
        self.valve_close() # stop wasting valve current
    def home(self):
        self.stop()
        self.up(2)
        self.lf(15)
    def mv_card(self, pos=12., hgt=1.5):
        self.grab()
        self.dn(2*hgt) # push hard to grab card
        self.up(hgt)
        self.rt(pos)
        self.dn(hgt)
        self.release()
    def mv_next(self, pos=12., hgt=1.5):
        self.up(hgt)
        self.lf(pos + 0.25)
    def move_card(self, pos=12., hgt=1.5):
        self.mv_card(pos=pos, hgt=hgt)
        self.mv_next(pos=pos, hgt=hgt)
    def sort(self, ncards, pos1=7., pos2=12., hgt=1.5, min_time=1.5):
        _, filename = tempfile.mkstemp()
        self.rt(pos2)
        t0 = time.time()
        findcard.webcam_to_file(filename)
        self.lf(pos2)
        for i in range(ncards):
            time.sleep(max(0,min_time - (time.time()-t0)))
            im = cv2.imread(filename)
            cards = self._finder.find(im)
            #cards = findcard.find_from_file(filename)
            #if any([x < 100 for x,y in cards]):
            if len(cards) >= 2:
                print('%d/%d' % (i+1,ncards), filename, ': back')
                pos = pos1
            else:
                print('%d/%d' % (i+1,ncards), filename, ': front')
                pos = pos2
            self.mv_card(pos, hgt=hgt)
            _, filename = tempfile.mkstemp()
            t0 = time.time()
            findcard.webcam_to_file(filename) # read while arm is away
            self.mv_next(pos=pos)
