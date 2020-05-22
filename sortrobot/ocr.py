from PIL import Image
import numpy as np
import pytesseract
from skimage.filters import rank
from skimage.morphology import disk
from skimage.util import img_as_ubyte


DEFAULT_OCR_CONFIG = r'-l eng --oem 3 --psm 7'
JUNK_CHR = '{([\\'

def _filter_text(text):
    if len(text) == 0:
        return text
    if not str.isalpha(text[0]):
        text = _filter_text(text[1:])
    split = text.split()
    split = [s for s in split if len(s) > 2 or \
             (str.isalpha(s[0]) and str.isalpha(s[-1]))]
    split = [s for s in split if len(s) > 1 or s not in 'Lh']
    return ' '.join(split)

def titlebar_to_text(title_bar, mana_px=100, verbose=False,
        ocr_config=DEFAULT_OCR_CONFIG, medfilt=False, preprocess=True):
    '''Convert title image to text, excluding mana symbols at far right.'''
    title = title_bar[:,:-mana_px].copy() # avoid changing original

    # Preprocess image
    if preprocess:
        if medfilt:
            ker = disk(2) # XXX hardcoded
            title = rank.median(img_as_ubyte(title), ker).astype(np.float)
        else:
            title = title.astype(np.float)
        title -= title.min()
        # Remove left-to-right lighting gradient
        mx = np.max(title, axis=0)
        poly = np.polyfit(np.arange(mx.size), mx, deg=5)
        sm = np.polyval(poly, np.arange(mx.size))
        sm.shape = (1,-1)
        title /= sm

    im = Image.fromarray(255 * title)
    text = pytesseract.image_to_string(im, config=ocr_config)
    if verbose:
        print('    OCR found:', [text])
    if len(text) == 0:
        # Sometimes tesseract does better with different prefiltering
        if preprocess and not medfilt:
            text = titlebar_to_text(title_bar, mana_px=mana_px,
                    ocr_config=ocr_config, medfilt=True, preprocess=True)
        elif preprocess:
            # Hail mary trying for no preprocessing
            text = titlebar_to_text(title_bar, mana_px=mana_px,
                    ocr_config=ocr_config, preprocess=False)
        assert len(text) > 0 # No dice on OCR

    # Clean up the answer a bit
    text = _filter_text(text)
    if verbose:
        print('    OCR cleaned:', [text])
    return text
