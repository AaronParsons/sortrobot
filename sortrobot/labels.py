import cPickle

def load(filename):
    '''Load a label dictionary from disk.'''
    f = open(filename, 'r')
    labdict = cPickle.load(f)
    return labdict
    
