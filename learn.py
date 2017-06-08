import chatter
import sys

c = chatter.Chatter(sys.argv[1]+".d")

for l in open(sys.argv[1], 'r'):
	c.learn(l)

c.close()
