import chatter
import sys

c = chatter.Chatter(sys.argv[1]+".d", writeback=True)

print("Learning...")
for l in open(sys.argv[1], 'r'):
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
