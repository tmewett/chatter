import random
import shelve

def _choices(choices):
    """Choose an item randomly. choices is a sequence of (item, weight)"""
    total = sum(w for c, w in choices)
    r = random.uniform(0, total)
    upto = 0
    for c, w in choices:
        if upto + w >= r:
            return c
        upto += w
    assert False

class MarkovChain():

    def __init__(self, name, writeback=False):
        self.brain = shelve.open(name, writeback=writeback)
        self.states = self.brain.keys()

    def observe(self, state, nextst, n=1):
        if n == 0: return
        links = self.brain.get(state, dict())
        if nextst not in links.keys():
            if n < 1: return
            links[nextst] = n
        else:
            links[nextst] += n
            # Delete the entry if the weight is now invalid
            if links[nextst] < 1:
                del links[nextst]

        self.brain[state] = links

    def forget(self, state, *nextsts):
        links = self.brain[state]
        for st in nextsts:
            if st not in links: continue
            del links[pos]
        self.brain[state] = links

    def findnext(self, state):
        links = self.brain[state]
        pairs = links.items()
        return _choices(tuple(pairs))

    def count(self, state):
        if state in self.states:
            links = self.brain[state]
            c = sum(links.values())
        else:
            c = 0
        return c

    def close(self):
        self.brain.close()

    def sync(self):
        self.brain.sync()
