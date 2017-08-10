import random
import re
import os.path
from itertools import count, chain
from os import mkdir
from time import time
from .markov import MarkovChain, _choices

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

    def __init__(self, name, nosave=False):
        """Opens the Chatter database directory *name*, creating it if
        necessary. *writeback* is passed to *shelve.open*, which causes
        all DB reads/writes to be cached in memory."""
        if not os.path.exists(name):
            mkdir(name)
        #~ Four Markov chains (more descriptively, random mappings) are used:
        #~ fore: norm seq -> word
        #~ back: norm seq -> word
        #~ seed: norm -> next word
        #~ case: norm -> corresponding word
        self.fore = MarkovChain(os.path.join(name, "fore.db"))
        self.back = MarkovChain(os.path.join(name, "back.db"))
        self.case = MarkovChain(os.path.join(name, "case.db"))
        self.seed = MarkovChain(os.path.join(name, "seed.db"))
        self.chains = (self.fore, self.back, self.case, self.seed)

        self.nosave = nosave
        self.lastsave = time()
        self.writes = 0

    def keyword(self, norms):
        """Return an 'interesting' learned norm in the sequence *norms*,
        or None. Currently it chooses randomly, preferring less
        frequently-observed ones."""
        counts = ((nm, self.case.count(nm)) for nm in norms)
        counts = dict(c for c in counts if c[1] > 0)
        if len(counts) == 0:
            return None
        maxi = max(counts.values())
        weights = [(k, 1/v) for k, v in counts.items()]
        return _choices(weights)

    def _seed(self, norm):
        """Get a random (w1, w2) such that w1's normalized form is norm"""
        word = self.case.findnext(norm)
        return word, self.seed.findnext(norm)

    def learn(self, line):
        """Learn *line*, updating the model."""
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
            self.seed.observe(norms[i], words[i+2])

        self.writes += 1
        if not self.nosave and time() > self.lastsave+300 and self.writes > 10:
            self.save()
            self.lastsave = time()
            self.writes = 0

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
        """Generate a sentence, sharing a word with *line* if possible"""
        norms = [_normalize(w) for w in line.split()]
        keyw = self.keyword(norms)
        if not keyw:
            # no keyword? pick a random norm
            allnorms = tuple(self.case.states)
            keyw = random.choice(allnorms)
        seed = self._seed(keyw)
        return self._generate(seed)

    def save(self):
        "Syncs the database shelves if *writeback* was True on init."
        for db in self.chains:
            db.save()

__all__ = ["Chatter"]
