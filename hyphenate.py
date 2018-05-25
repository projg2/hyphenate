#!/usr/bin/env python

import argparse
import codecs
import locale
import re
import sys

import pyphen


def main(argv):
    locale.setlocale(locale.LC_ALL, '')
    deflang = locale.getlocale(locale.LC_COLLATE)[0] or 'en_GB'
    defenc = locale.nl_langinfo(locale.CODESET) or 'utf-8'

    argparser = argparse.ArgumentParser()

    argparser.add_argument(
        '-e', '--encoding', action='store',
        dest='encoding',
        help='Character encoding to use for I/O (locale default: %s)' % defenc)
    argparser.add_argument(
        '-l', '--language', action='store',
        dest='language',
        help='The language to lookup the hyphenation rules for '
             '(locale default: %s)' % deflang)
    argparser.add_argument(
        '-t', '--text', action='store_const',
        dest='type', const='text',
        help='Treat the following files as plain text files')
    argparser.add_argument('file', nargs='+')

    argparser.set_defaults(
        encoding=defenc,
        language=deflang,
        type='text')

    opts = argparser.parse_args()

    try:
        h = pyphen.Pyphen(lang=opts.language)
    except IOError as e:
        argparser.error('unknown language: %s (%s)' % (
            opts.language, str(e)))

    for path in opts.file:
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
