import random
import json

def read_json(filename):
    '''Read a scryfall json file.'''
    with open(filename) as f:
        info = json.load(f)
    return info

def random_filename(lim=2**31):
    '''Generate a random (hex) filename string.'''
    hexstr = hex(random.randint(0,lim))[2:]
    hexstr = ('0' * 8 + hexstr)[-8:]
    return hexstr + '.jpg'
