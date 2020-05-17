import picamera
import picamera.array
from fractions import Fraction

class Camera:
    def __init__(self, size=(640,480), framerate=4, rotation=180, 
            shutter_speed=250000, iso=400):
        self.camera = picamera.PiCamera()
        self.camera.resolution = size
        self.camera.framerate = framerate
        self.camera.rotation = rotation
        self.camera.shutter_speed = shutter_speed
        self.camera.iso = iso
    def rgb_to_file(self, filename):
        self.camera.capture(filename)
        return filename
    def rgb_to_array(self):
        stream = picamera.array.PiRGBArray(self.camera)
        self.camera.capture(stream, 'rgb')
        return stream
