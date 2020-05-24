from .cardface import extract_titlebar
from .ocr import titlebar_to_text
from skimage.transform import rotate
from .lookup import search

def identify(filename, precrop=(80,80,160,570), verbose=False):
    '''Use various setting to try to get a clean OCR of a card and
    look it up on the web.'''
    def echo(*args):
        if verbose: print(*args)
    try:
        echo('    LABEL: using cropping:', precrop)
        title_bar = extract_titlebar(filename, precrop=precrop,
                                     verbose=verbose)
    except(AssertionError):
        echo('    LABEL: retrying titlebar extraction w/o cropping.')
        try:
            title_bar = extract_titlebar(filename, verbose=verbose)
        except(AssertionError):
            echo('    LABEL: Failed to find title bar.')
            return {}
    try:
        text = titlebar_to_text(title_bar, verbose=verbose)
    except(AssertionError):
        from skimage.transform import rotate
        text = ''
        for ang in [-0.5, 0.5, -1,1,-2,2]:
            echo('    LABEL: brute force rotate {} deg'.format(ang))
            rot_title_bar = rotate(title_bar, ang)
            try:
                text = titlebar_to_text(rot_title_bar,verbose=verbose)
                title_bar = rot_title_bar
                break
            except(AssertionError):
                pass
        if len(text) == 0:
            echo('    LABEL: brute force rotate failed.')
            return {}
    try:
        info = search(text, verbose=verbose)
        echo('    LABEL: found entry for {}'.format(info['name']))
        return info
    except(ValueError):
        echo('    {} lookup failed'.format(text))
        return {}


def label_color(info):
    '''Return a color label from json info.'''
    key = 'color_identity'
    if not key in info:
        return 'unknown'
    color = info[key]
    if len(color) == 0:
        return 'none'
    elif len(color) > 1:
        return 'multi'
    else:
        return color[0]

def label_type(info):
    '''Return a mana label from json info.'''
    key = 'type_line'
    if not key in info:
        return 'unknown'
    line = info[key].lower()
    if line.startswith('creature'):
        return 'creature'
    elif line.startswith('instant') or line.startswith('enchantment') \
            or line.startswith('sorcery'):
        return 'spell'
    elif line.find('land'):
        return 'land'
    else:
        return 'other'

def label_rarity(info):
    '''Return rarity label from json info.'''
    key = 'rarity'
    if not key in info:
        return 'unknown'
    rarity = info[key]
    return rarity

