for l in open("messages.txt", 'r'):
	l=l[2:]
	n=len(l)
	if n > 20 and n < 150: print(l, end="")
