from pickle import dumps, loads
from zlib import compress, decompress
from os.path import exists


class Store(dict):

    def __init__(self, fname, *args):
        super().__init__(*args)
        self.filename = fname

    def save(self):
        with open(self.filename, 'bw') as f:
            f.write(compress(dumps(self)))


def load(fname):
    if exists(fname):
        with open(fname, 'br') as f:
            return loads(decompress(f.read()))
    else:
        return Store(fname)
