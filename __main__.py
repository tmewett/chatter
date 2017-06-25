from . import utils
from sys import argv

if len(argv) > 1 and hasattr(utils, argv[1]):
	getattr(utils, argv[1])(*argv[2:])
else:
	print("python -m chatter talk <dir> | learn <file>")
