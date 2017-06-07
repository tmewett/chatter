import random
import re
import shelve


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

    def __init__(self, name):
        self.brain = shelve.open(name+".db")

    def observe(self, state, nextst):
        links = self.brain.setdefault(state, ([],[]) )
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
    words.append("end")
    for n in range(len(norms)-1):
        chain.observe(" ".join(norms[n:n+2]), words[n+2])

# Continue the sentence from the two given norms.
# Returns a list of words. The norms must have been observed already
def _find_seq(chain, nm1, nm2):
    words = []
    norms = [nm1, nm2]
    i = 0
    while True:
        nextw = chain.findnext(" ".join(norms[i:i+2]))
        if nextw == "end": break
        words.append(nextw)
        norms.append(_normalize(nextw))
        i += 1
    return words

def _clean(lst):
    for s in lst:
        if "://" in s: continue
        yield s

def _normalize(s):
    #~ s = re.sub(r"([^\w\.])", "\\1", s)
    s = re.sub(r"(\W){2,}", "\\1", s)
    return s.upper()

class Chatter():

    def __init__(self, name):
        self.fore = MarkovChain(name+"_fore")
        self.back = MarkovChain(name+"_back")
        self.case = MarkovChain(name+"_case")
        self.seed = MarkovChain(name+"_seed")

    # Returns a random learned norm in the list, or None
    def _keyword(self, norms):
        norms = norms.copy()
        allnorms = self.case.brain.keys()

        for nm in norms:
            if nm not in allnorms:
                norms.remove(nm)

        if norms:
            return random.choice(norms)
        else:
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


        self.case.observe("start", words[0])
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
        forewd = _find_seq(self.fore, start[0], start[1])
        backwd = _find_seq(self.back, start[1], start[0])
        phrase = (*reversed(backwd), wordpair, *forewd)
        return " ".join(phrase)

    def respond(self, line):
        norms = [_normalize(w) for w in line.split()]
        keyw = self._keyword(norms)
        if not keyw:
            # no keywords? generate a sentence from the beginning
            keyw = "start"
        seed = self._seed(keyw)
        return self.generate(seed)

    def close(self):
        for db in (self.fore, self.back, self.case, self.seed):
            db.close()
