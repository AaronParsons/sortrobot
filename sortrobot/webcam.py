import cv2
import subprocess
import tempfile

def to_file(filename, brightness=20, block=False):
    cmd = 'fswebcam -s brightness=%d -q --no-banner %s' % (brightness, filename)
    p = subprocess.Popen(cmd, shell=True)
    if block: p.wait()
    else: return p

def read(filename=None, brightness=20):
    if filename is None:
        _, filename = tempfile.mkstemp()
    webcam_to_file(to_file, brightness=brightness, block=True)
    im = cv2.imread(to_file)
    return {filename:im}
        
