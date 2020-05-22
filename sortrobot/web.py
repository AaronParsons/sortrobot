import urllib.parse
import urllib.request
import json

URL = 'https://api.scryfall.com/cards/named'

def lookup(title, exact=True, verbose=False):
    '''Look up the title on scryfall.'''
    # Build request
    if exact:
        data = {'exact': title}
    else:
        data = {'fuzzy': title}
    url_data = urllib.parse.urlencode(data)
    request = URL + '?' + url_data
    # Send request
    try:
        with urllib.request.urlopen(request) as response:
            page = response.read()
            info = json.loads(page)
            return info
    except(urllib.error.HTTPError):
        # If we fail, try an inexact match
        if exact:
            if verbose:
                print('    LOOKUP: Trying fuzzy match.')
            return lookup(title, exact=False, verbose=verbose)
        else:
            raise ValueError("Couldn't find card '{}'".format(title))
