import random
from itertools import count, chain
import re
import shelve
from os import mkdir
import os.path


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

    def close(self):
        self.brain.close()

    def sync(self):
        self.brain.sync()


def _find_seq(chain, nms):
    """Continue the sentence from the two given norms.
    Returns a list of words. The norms must have been observed already"""
    words = []
    norms = nms.copy()
    for i in count(0):
        nextw = chain.findnext(" ".join(norms[i:i+2]))
        if nextw == None: break
        words.append(nextw)
        norms.append(_normalize(nextw))
    return words

def _clean(lst):
    for s in lst:
        if "://" in s: continue
        yield s

def _normalize(s):
    # remove duplicate non-word chars
    s = re.sub(r"(\W){2,}", "\\1", s)
    return s.upper()

class Chatter():
    """Chatter uses four Markov chains (more descriptively, random mappings):
    fore: norm seq -> word
    back: norm seq -> word
    seed: word -> next word
    case: norm -> corresponding word"""

    def __init__(self, name, writeback=False):
        if not os.path.exists(name):
            mkdir(name)
        self.fore = MarkovChain(os.path.join(name, "fore.db"), writeback)
        self.back = MarkovChain(os.path.join(name, "back.db"), writeback)
        self.case = MarkovChain(os.path.join(name, "case.db"), writeback)
        self.seed = MarkovChain(os.path.join(name, "seed.db"), writeback)

    def keyword(self, norms):
        """"Return a random learned norm in the list, or None"""
        norms = norms.copy()
        random.shuffle(norms)
        allnorms = self.case.states

        for nm in norms:
            if nm in allnorms:
                return nm
        return None

    def _seed(self, norm):
        """Get a random (w1, w2) such that w1's normalized form is norm"""
        word = self.case.findnext(norm)
        return word, self.seed.findnext(word)

    def learn(self, line):
        words = list(_clean(line.split()))
        if len(words) < 2:
            # We can't learn without at least 2 words
            return
        norms = [_normalize(w) for w in words]

        # None signifies the end of the phrase
        words.insert(0, None)
        words.append(None)
        for i in range(len(norms)-1):
            self.fore.observe(" ".join(norms[i:i+2]), words[i+3])
            self.back.observe(" ".join(reversed(norms[i:i+2])), words[i])
            # We can't learn the case or seed with the last word. Otherwise
            # _seed might give us an ending word pair
            self.case.observe(norms[i], words[i+1])
            self.seed.observe(words[i+1], words[i+2])

    def _generate(self, wordpair):
        """Generate a sentence which includes the tuple wordpair.
        Note: raises KeyError if wordpair hasn't been observed"""
        start = [_normalize(w) for w in wordpair]
        forewd = _find_seq(self.fore, start)
        backwd = _find_seq(self.back, start[::-1])
        backwd.reverse()
        phrasei = chain(backwd, wordpair, forewd)
        return " ".join(phrasei)

    def respond(self, line=""):
        """Generate a sentence, sharing a word with line if possible"""
        norms = [_normalize(w) for w in line.split()]
        keyw = self.keyword(norms)
        if not keyw:
            # no keyword? pick a random norm
            allnorms = tuple(self.case.states)
            keyw = random.choice(allnorms)
        seed = self._seed(keyw)
        return self._generate(seed)

    def close(self):
        for db in (self.fore, self.back, self.case, self.seed):
            db.close()

    def sync(self):
        for db in (self.fore, self.back, self.case, self.seed):
            db.sync()
