#!/usr/bin/env python2

import codecs
import locale
import optparse
import re
import sys

import pyphen


class MultiArgOptionParser(optparse.OptionParser):
	@staticmethod
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

	def parse_args(self, argv, values = None):
		for arggroup in self.split_args(argv):
			(values, args) = optparse.OptionParser.parse_args(self, arggroup, values)
			yield (values, args)


def reset_opts(opt, optstr, values, parser):
	parser.values.__init__(defaults = parser.defaults)


def main(argv):
	locale.setlocale(locale.LC_ALL, '')
	deflang = locale.getlocale(locale.LC_COLLATE)[0] or 'en_GB'
	defenc = locale.nl_langinfo(locale.CODESET) or 'utf-8'

	argparser = MultiArgOptionParser(
			usage='%prog [opts1] file1 [...] [[opts2] file2 [...]] [...]')

	argparser.add_option('-e', '--encoding', action='store',
			dest='encoding',
			help='Character encoding to use for I/O (locale default: %s)' % defenc)
	argparser.add_option('-l', '--language', action='store',
			dest='language',
			help='The language to lookup the hyphenation rules for (locale default: %s)' % deflang)
	argparser.add_option('-r', '--reset', action='callback',
			callback=reset_opts,
			help='Reset the options to defaults (forfeit previous options)')
	argparser.add_option('-t', '--text', action='store_const',
			dest='type', const='text',
			help='Treat the following files as plain text files')

	argparser.set_defaults(
			encoding=defenc,
			language=deflang,
			type='text')

	# Parse the arguments in series in order to apply the preceeding
	# options to the filenames.
	opts = None
	for argn, (opts, args) in enumerate(argparser.parse_args(argv[1:])):
		if not args:
			if argn == 0:
				argparser.error('no file specified')
				return 1
			else:
				sys.stderr.write('Warning: options passed after the last file have no effect.\n')
		try:
			h = pyphen.Pyphen(lang=opts.language)
		except IOError as e:
			argparser.error('unknown language: %s (%s)' % (opts.language, str(e)))
			# well, this probably won't be reached but keep it safe
			continue

		for path in args:
			try:
				f = codecs.open(path, 'r+', opts.encoding)
			except IOError as e:
				sys.stderr.write('open() failed: %s\n' % str(e))
			except LookupError as e:
				argparser.error(str(e))
			else:
				if opts.type == 'text':
					hyph_text(f, h)

	return 0


def hyph_text(f, h):
	wordregex = re.compile('(?u)(\W+)')

	lines = f.readlines()

	for i, l in enumerate(lines):
		words = wordregex.split(l)
		for j, w in enumerate(words):
			if j % 2 == 0:  # even ones are separators
				words[j] = h.inserted(w, hyphen=u'\u00ad')  # soft hyphen
		lines[i] = u''.join(words)

	f.seek(0)
	f.truncate()
	f.writelines(lines)


if __name__ == "__main__":
	sys.exit(main(sys.argv))
