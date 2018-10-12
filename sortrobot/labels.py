import cPickle

def load(filename):
    f = open(filename, 'r')
    labdict = cPickle.load(f)
    return labdict
    
