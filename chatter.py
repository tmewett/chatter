import random
from itertools import count
import re
import shelve
from os import mkdir
import os.path


def _choices(choices):
    choices = tuple(choices) # we have to iterate twice
    total = sum(w for c, w in choices)
    r = random.uniform(0, total)
    upto = 0
    for c, w in choices:
        if upto + w >= r:
            return c
        upto += w
    assert False

class MarkovChain():

    def __init__(self, name, wb):
        self.brain = shelve.open(name+".db", writeback=wb)

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
        return _choices(zip(*links))

    def close(self):
        self.brain.close()


def _observe_seq(chain, words, norms):
    words = words.copy()
    words.append("%END%")
    for n in range(len(norms)-1):
        chain.observe(" ".join(norms[n:n+2]), words[n+2])

# Continue the sentence from the two given norms.
# Returns a list of words. The norms must have been observed already
def _find_seq(chain, nms):
    words = []
    norms = nms.copy()
    for i in count(0):
        nextw = chain.findnext(" ".join(norms[i:i+2]))
        if nextw == "%END%": break
        words.append(nextw)
        norms.append(_normalize(nextw))
    return words

def _clean(lst):
    for s in lst:
        if "://" in s or s == "%END%": continue
        yield s

def _normalize(s):
    #~ s = re.sub(r"([^\w\.])", "\\1", s)
    s = re.sub(r"(\W){2,}", "\\1", s)
    return s.upper()

class Chatter():

    def __init__(self, name, writeback=False):
        if not os.path.exists(name):
            mkdir(name)
        self.fore = MarkovChain(os.path.join(name, "fore"), wb=writeback)
        self.back = MarkovChain(os.path.join(name, "back"), wb=writeback)
        self.case = MarkovChain(os.path.join(name, "case"), wb=writeback)
        self.seed = MarkovChain(os.path.join(name, "seed"), wb=writeback)

    # Returns a random learned norm in the list, or None
    def _keyword(self, norms):
        norms = norms.copy()
        random.shuffle(norms)
        allnorms = self.case.brain.keys()

        for nm in norms:
            if nm in allnorms:
                return nm
        return None

    def _seed(self, norm):
        word = self.case.findnext(norm)
        return word+" "+self.seed.findnext(word)

    def learn(self, line):
        words = list(_clean(line.split()))
        if len(words) < 2:
            # We can't learn without at least 2 words
            return
        norms = [_normalize(w) for w in words]


        self.case.observe("%START%", words[0])
        # -1 so we don't learn the case of the last word. Otherwise
        # we will have problems seeding. TODO fix?
        for i in range(len(norms)-1):
            self.case.observe(norms[i], words[i])

        for i in range(len(words)-1):
            self.seed.observe(words[i], words[i+1])

        _observe_seq(self.fore, words, norms)
        words.reverse()
        norms.reverse()
        _observe_seq(self.back, words, norms)

    # Generate a sentence which includes wordpair, which must have been observed
    def generate(self, wordpair):
        start = [_normalize(w) for w in wordpair.split()]
        forewd = _find_seq(self.fore, start)
        backwd = _find_seq(self.back, start[::-1])
        phrase = (*reversed(backwd), wordpair, *forewd)
        return " ".join(phrase)

    def respond(self, line):
        norms = [_normalize(w) for w in line.split()]
        keyw = self._keyword(norms)
        if not keyw:
            # no keywords? generate a sentence from the beginning
            keyw = "%START%"
        seed = self._seed(keyw)
        return self.generate(seed)

    def close(self):
        for db in (self.fore, self.back, self.case, self.seed):
            db.close()
