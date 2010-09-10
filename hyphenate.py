#!/usr/bin/python2

import codecs, re, sys
import optparse

from hyphenator import Hyphenator

def split_args(argv):
	out = []
	gotfile = False
	for a in argv:
		if a.startswith('-'):
			if gotfile:
				yield out
				out = []
				gotfile = False
		else:
			gotfile = True
		out.append(a)
	if out:
		yield out

def main(argv):
	argparser = optparse.OptionParser(
			usage='%prog [opts1] file1 [...] [[opts2] file2 [...]] [...]')
	argparser.add_option('-t', '--text', action='store_const',
			dest='type', const='text',
			help='Treat the following files as plain text files')
	argparser.set_defaults(type='text')

	# Parse the arguments in series in order to apply the preceeding
	# options to the filenames.
	opts = None
	for arggroup in split_args(argv[1:]):
		(opts, args) = argparser.parse_args(arggroup, opts)
		for path in args:
			try:
				f = codecs.open(path, 'r+', 'utf-8')
			except IOError as e:
				sys.stderr.write('open() failed: %s\n' % str(e))
			else:
				if opts.type == 'text':
					hyph_text(f)

	return 0

def hyph_text(f):
	h = Hyphenator('/usr/share/myspell/hyph_pl_PL.dic', 3, 3)
	wordregex = re.compile('(?u)(\W+)')

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
