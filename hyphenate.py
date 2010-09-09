#!/usr/bin/python2

import codecs, re, sys
import argparse

from hyphenator import Hyphenator

class EncodedFileType(argparse.FileType):
	def __init__(self, mode='r', encoding=None, errors=None, bufsize=None):
		argparse.FileType.__init__(self, mode, bufsize)
		self._encoding = encoding
		self._errors = errors

	def __call__(self, string):
		if self._bufsize:
			return codecs.open(string, self._mode, self._encoding,
				self._errors, self._bufsize)
		else:
			return codecs.open(string, self._mode, self._encoding,
				self._errors)

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
	argparser = argparse.ArgumentParser()
	argparser.add_argument('-t', '--text', action='store_const',
			dest='type', const='text',
			help='Treat the following files as plain text files')
	argparser.add_argument('files', metavar='file', nargs='+',
			type=EncodedFileType('r+', 'utf-8'),
			help='The file(s) to process')
	argparser.set_defaults(type='text')

	# Ok, argparse is stupid and doesn't like mixing positional args
	# with optional ones. So we parse them in series.
	args = None
	for arggroup in split_args(argv[1:]):
		args = argparser.parse_args(arggroup, args)
		for f in args.files:
			if args.type == 'text':
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
