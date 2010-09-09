#!/usr/bin/python2

import codecs, re, sys

from hyphenator import Hyphenator

def main(argv):
	h = Hyphenator('/usr/share/myspell/hyph_pl_PL.dic', 3, 3)
	wordregex = re.compile('(?u)(\W+)')

	for fn in argv[1:]:
		f = codecs.open(fn, 'r+', 'utf-8')
		lines = f.readlines()

		for i, l in enumerate(lines):
			words = wordregex.split(l)
			for j, w in enumerate(words):
				if i%2 == 0: # even ones are separators
					words[j] = h.inserted(w, u'\u00ad') # soft hyphen
			lines[i] = u''.join(words)

		f.seek(0)
		f.truncate()
		f.writelines(lines)

if __name__ == "__main__":
	sys.exit(main(sys.argv))
