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
        paths, weights = self.brain.get(state, ([],[]))
        if nextst not in paths:
            if n < 1: return
            paths.append(nextst)
            weights.append(n)
        else:
            pos = paths.index(nextst)
            weights[pos] += n
            # Delete the entry if the weight is now invalid
            if weights[pos] < 1:
                del paths[pos]
                del weights[pos]

        self.brain[state] = (paths, weights)

    def forget(self, state, *nextsts):
        paths, weights = self.brain[state]
        for st in nextsts:
            if st not in paths: continue
            pos = paths.index(st)
            del paths[pos]
            del weights[pos]
        self.brain[state] = (paths, weights)

    def findnext(self, state):
        links = self.brain[state]
        pairs = zip(*links)
        return _choices(tuple(pairs))

    def count(self, state):
        if state in self.brain:
            links = self.brain[state]
            c = sum(links[1])
        else:
            c = 0
        return c

    def close(self):
        self.brain.close()

    def sync(self):
        self.brain.sync()
