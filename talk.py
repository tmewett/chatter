import chatter
import sys

c = chatter.Chatter(sys.argv[1])

while True:
	print(c.respond(input("> ")))
