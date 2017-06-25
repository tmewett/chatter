from chatter import Chatter

def learn(fn):
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
	c = Chatter(name)

	while True:
		print(c.respond(input("> ")))
