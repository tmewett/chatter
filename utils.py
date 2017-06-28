from .chatter import Chatter

def learn(fn):
	"""Learns each line of the file named *fn* into the Chatter DB 'fn.d'."""
	c = Chatter(fn+".d", writeback=True)

	print("Learning...")
	for l in open(fn, 'r'):
		c.learn(l)

	print("Writing to disk...")
	c.sync()

	# the seed db can get large, so shrink it
	db = c.seed.brain.dict
	if hasattr(db, "reorganize"):
		print("Reorganizing...")
		db.reorganize()
	else:
		print("Skipped reorganizing (gdbm unavailable)")

	c.close()

def talk(name):
	"""Start a prompt to talk with the Chatter DB *name*."""
	c = Chatter(name)

	while True:
		print(c.respond(input("> ")))
