from .chatter import Chatter

def learn(fn):
	"""Learns each line of the file named *fn* into the Chatter DB 'fn.d'."""
	c = Chatter(fn+".d", writeback=True)

	# Learn directly to the shelf cache (a dict) for speed
	for attr in "fore back case seed".split():
		chain = getattr(c, attr)
		chain._brain = chain.brain
		chain.brain = chain.brain.cache

	print("Learning...")
	for l in open(fn, 'r'):
		c.learn(l)

	print("Writing to disk...")

	# Replace shelf before we close
	for attr in "fore back case seed".split():
		chain = getattr(c, attr)
		chain.brain = chain._brain
		del chain._brain

	c.sync()
	c.close()

def talk(name):
	"""Start a prompt to talk with the Chatter DB *name*."""
	c = Chatter(name)

	while True:
		print(c.respond(input("> ")))
