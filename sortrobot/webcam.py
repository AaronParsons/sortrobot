import cv2
import subprocess
import tempfile

def to_file(filename, size=(1280,720), brightness=100, block=False):
    cmd = 'fswebcam -r %dx%d -s brightness=%d -q --no-banner %s' % (size + (brightness, filename))
    p = subprocess.Popen(cmd, shell=True)
    if block: p.wait()
    else: return p

def read(filename=None, size=(1280,720), brightness=100):
    if filename is None:
        _, filename = tempfile.mkstemp()
    to_file(filename, size=size, brightness=brightness, block=True)
    im = cv2.imread(filename)
    return {filename:im}
        
