#!/usr/bin/python2

import codecs, re, sys
import optparse

from hyphenator import Hyphenator

def split_args(argv):
	out = []
	gotfile = False
	for i, a in enumerate(argv):
		if a.startswith('-'):
			if a == '--':
				out.extend(argv[i:])
				break
			elif gotfile:
				yield out
				out = []
				gotfile = False
		else:
			gotfile = True
		out.append(a)
	yield out

def main(argv):
	argparser = optparse.OptionParser(
			usage='%prog [opts1] file1 [...] [[opts2] file2 [...]] [...]')

	argparser.add_option('-e', '--encoding', action='store',
			dest='encoding',
			help='Character encoding to use for I/O (default: utf-8)')
	argparser.add_option('-t', '--text', action='store_const',
			dest='type', const='text',
			help='Treat the following files as plain text files')

	argparser.set_defaults(
			encoding='utf-8',
			type='text')

	# Parse the arguments in series in order to apply the preceeding
	# options to the filenames.
	opts = None
	for argn, arggroup in enumerate(split_args(argv[1:])):
		(opts, args) = argparser.parse_args(arggroup, opts)
		if not args:
			if argn == 0:
				argparser.error('no file specified')
				return 1
			else:
				sys.stderr.write('Warning: options passed after the last file have no effect.\n')
		for path in args:
			try:
				f = codecs.open(path, 'r+', opts.encoding)
			except IOError as e:
				sys.stderr.write('open() failed: %s\n' % str(e))
			except LookupError as e:
				argparser.error(str(e))
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
