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

    def observe(self, state, nextst):
        links = self.brain.get(state, ([],[]) )
        if nextst not in links[0]:
            links[0].append(nextst)
            links[1].append(1)
        else:
            pos = links[0].index(nextst)
            links[1][pos] += 1
        self.brain[state] = links

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
