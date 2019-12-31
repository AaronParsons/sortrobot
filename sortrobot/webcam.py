import cv2
import subprocess
import tempfile

def to_file(filename, brightness=100, block=False):
    cmd = 'fswebcam -r 1280x720 -s brightness=%d -q --no-banner %s' % (brightness, filename)
    p = subprocess.Popen(cmd, shell=True)
    if block: p.wait()
    else: return p

def read(filename=None, brightness=100):
    if filename is None:
        _, filename = tempfile.mkstemp()
    to_file(filename, brightness=brightness, block=True)
    im = cv2.imread(filename)
    return {filename:im}
        
