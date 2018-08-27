from __future__ import print_function
import rrb3, time, numpy, os, tempfile
import findcard

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
    def __init__(self, Vin=6., Vmotor=6.):
        self._driver = rrb3.RRB3(Vin,Vmotor)
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
        print('UP:', dt)
        self._send_cmd(m1=UP_SPEED)
        time.sleep(dt)
        self._send_cmd(m1=0.)
    def dn(self, degrees):
        dt = degrees * LIFT_TIME
        print('DN:', dt)
        self._send_cmd(m1=-DN_SPEED)
        time.sleep(dt)
        self._send_cmd(m1=0.)
    def lf(self, inches):
        dt = numpy.polyval(SLIDE_POLY, inches) * SLIDE_TIME
        print('LF:', dt)
        self._send_cmd(m2=-SLIDE_LF_SPEED)
        time.sleep(dt)
        self._send_cmd(m2=0)
    def rt(self, inches):
        dt = numpy.polyval(SLIDE_POLY, inches) * SLIDE_TIME
        print('RT:', dt)
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
        self.valve_close() # hold hard
    def hold(self):
        self.pump_on()
        self.valve_open() # release pressure
    def put(self, dt=5.):
        self.valve_open() # release pressure
        self.pump_off()
        time.sleep(dt)
        self.valve_open() # stop wasting valve current
    def home(self):
        self.stop()
        self.up(2)
        self.lf(15)
    def mv_card(self, pos=12., grab=.15, wait=1.5):
        self.dn(3.25)
        self.grab()
        time.sleep(grab)
        self.put(0)
        self.up(.4)
        time.sleep(.75)
        self.up(.5)
        self.rt(pos)
        self.dn(1.)
        time.sleep(wait)
    def mv_next(self, pos=12.):
        self.up(1.)
        self.lf(pos + 0.25)
    def move_card(self, pos=12., grab=.15, wait=1.5):
        self.mv_card(pos=pos, grab=grab, wait=wait)
        self.mv_next(pos=pos)
    def sort(self, ncards, pos1=6., pos2=12., grab=.15, wait=1.5):
        self.rt(pos2)
        _, filename = tempfile.mkstemp()
        im = findcard.read_webcam(filename)
        self.lf(pos2)
        for i in range(ncards):
            cards = findcard.find(im)
            print(cards)
            if any([x < 100 for x,y in cards]):
                print('FOUND: back')
                pos = pos1
            else:
                print('FOUND: front')
                pos = pos2
            self.mv_card(pos, grab=grab, wait=0)
            im = findcard.read_webcam(filename, wait=wait) # read while arm is away
            self.mv_next(pos=pos)
        

r = SortRobot()
import IPython; IPython.embed()
