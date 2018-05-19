import random
import re
import os.path
from itertools import count, chain
from os import mkdir
from .markov import MarkovChain, _choices


class Chatter():

    def __init__(self, name, writeback=False):
        """Opens the Chatter database directory *name*, creating it if
        necessary. *writeback* is passed to *shelve.open*, which causes
        all DB reads/writes to be cached in memory."""
        if not os.path.exists(name):
            mkdir(name)
        #~ Four Markov chains (more descriptively, random mappings) are used:
        #~ fore: norm seq -> word
        #~ back: norm seq -> word
        #~ seed: word -> next word
        #~ case: norm -> corresponding word
        self.fore = MarkovChain(os.path.join(name, "fore.db"), writeback)
        self.back = MarkovChain(os.path.join(name, "back.db"), writeback)
        self.case = MarkovChain(os.path.join(name, "case.db"), writeback)
        self.seed = MarkovChain(os.path.join(name, "seed.db"), writeback)

    def keyword(self, norms):
        """Return an 'interesting' learned norm in the sequence *norms*,
        or None. Currently it chooses randomly, preferring less
        frequently-observed ones."""
        normset = set(norms)
        normset.update(self.supernorm(nm) for nm in norms)
        counts = ((nm, self.case.count(nm)) for nm in normset)
        counts = dict(c for c in counts if c[1] > 0)
        if len(counts) == 0:
            return None
        maxi = max(counts.values())
        weights = [(k, 1/v) for k, v in counts.items()]
        return _choices(weights)

    def splitwords(self, line):
        """Override this method to change how input lines are split
        into words and sanitised for learning. Returns a list of strings"""
        # just get rid of URLs by default
        return [w for w in string.split() if "://" not in w]

    def normalise(self, s):
        """Override this method to change how words are 'hashed' to
        disregard information like case. This can return any hashable, picklable type"""
        # remove duplicate non-word chars
        s = re.sub(r"(\W){2,}", "\\1", s)
        return s.upper()

    def supernorm(self, s):
        """Override this method to change how norms are 'hashed' further
        to an even smaller set. (Only used in keyword extraction, may be removed)"""
        # remove all non-words
        s = re.sub(r"\W+", "", s)
        return s

    def _seed(self, norm):
        """Get a random (w1, w2) such that w1's normalized form is norm"""
        word = self.case.findnext(norm)
        return word, self.seed.findnext(norm)

    def learn(self, line):
        """Learn *line*, updating the model."""
        words = self.splitwords(line)
        if len(words) < 2:
            # We can't learn without at least 2 words
            return
        norms = [self.normalise(w) for w in words]

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

    def _find_seq(self, chain, nms):
        """Continue the sentence from the two given norms, by walking through *chain*.
        Returns a list of words. The norms must have been observed already"""
        words = []
        norms = nms.copy()
        for i in count(0):
            nextw = chain.findnext(" ".join(norms[i:i+2]))
            if nextw == None: break
            words.append(nextw)
            norms.append(self.normalise(nextw))
        return words

    def _generate(self, wordpair):
        """Generate a sentence which includes the tuple wordpair.
        Note: raises KeyError if wordpair hasn't been observed"""
        start = [self.normalise(w) for w in wordpair]
        forewd = self._find_seq(self.fore, start)
        backwd = self._find_seq(self.back, start[::-1])
        backwd.reverse()
        phrasei = chain(backwd, wordpair, forewd)
        return " ".join(phrasei)

    def respond(self, line=""):
        """Generate a sentence, sharing a word with *line* if possible"""
        norms = [self.normalise(w) for w in line.split()]
        keyw = self.keyword(norms)
        if not keyw:
            # no keyword? pick a random norm
            allnorms = tuple(self.case.states)
            keyw = random.choice(allnorms)
        seed = self._seed(keyw)
        return self._generate(seed)

    def close(self):
        "Closes the database shelves, making the instance unusable."
        for db in (self.fore, self.back, self.case, self.seed):
            db.close()

    def sync(self):
        "Syncs the database shelves if *writeback* was True on init."
        for db in (self.fore, self.back, self.case, self.seed):
            db.sync()

__all__ = ["Chatter"]
