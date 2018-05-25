#!/usr/bin/env python3

import argparse
import codecs
import locale
import lxml.etree
import re
import shutil
import sys
import tempfile

import pyphen


wsregex = re.compile(r'(?u)(\s+)')
wordregex = re.compile('(?u)(\W+)')


def hyph_word(word, h, hyphen):
    """Return hyphenated version of word."""
    # do not hyphenate URLs
    if '://' in word:
        return word
    # split further on word characters
    words = wordregex.split(word)
    for j, w in enumerate(words):
        if j % 2 == 0:  # even ones are separators
            words[j] = h.inserted(words[j], hyphen)  # soft hyphen
    return u''.join(words)


def hyph_text_block(block, h):
    words = wsregex.split(block)
    for j, w in enumerate(words):
        if j % 2 == 0:  # even ones are separators
            words[j] = hyph_word(words[j], h, u'\u00ad')  # soft hyphen
    return u''.join(words)


def hyph_text(f, outf, h):
    for l in f:
        outf.write(hyph_text_block(l, h))


def hyph_xhtml_recursive(elem, h):
    # only hyphenate when we know it's safe
    tag = lxml.etree.QName(elem).localname
    if tag in ['body', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7',
            'dl', 'dt', 'dd', 'ul', 'ol', 'li', 'p', 'a', 'blockquote',
            'strong', 'em', 'cite', 'span']:
        if elem.text:
            elem.text = hyph_text_block(elem.text, h)
    elif tag in ['pre']:
        # skip hyphenation here, recursively
        return
    else:
        raise NotImplementedError(tag)

    for e in elem:
        hyph_xhtml_recursive(e, h)


def hyph_xhtml(f, outf, h):
    xhtml = lxml.etree.parse(f)
    html = xhtml.getroot()
    ns = lxml.etree.QName(html).namespace
    body = html.find(lxml.etree.QName(ns, 'body'))
    hyph_xhtml_recursive(body, h)
    outf.write(lxml.etree.tostring(xhtml, encoding='unicode'))


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

    typearg = argparser.add_mutually_exclusive_group()
    typearg.add_argument(
        '-t', '--text', action='store_const',
        dest='processor', const=hyph_text,
        help='Process files as plain text files (default)')
    typearg.add_argument(
        '-x', '--xhtml', action='store_const',
        dest='processor', const=hyph_xhtml,
        help='Process files as XHTML')

    argparser.add_argument('file', nargs='+')
    argparser.set_defaults(
        encoding=defenc,
        language=deflang,
        processor=hyph_text)

    opts = argparser.parse_args()

    try:
        h = pyphen.Pyphen(lang=opts.language)
    except IOError as e:
        argparser.error('unknown language: %s (%s)' % (
            opts.language, str(e)))

    for path in opts.file:
        try:
            with codecs.open(path, 'r', opts.encoding) as f:
                try:
                    with tempfile.NamedTemporaryFile(delete=False,
                            mode='w',
                            encoding=opts.encoding) as outf:
                        opts.processor(f, outf, h)
                    shutil.move(outf.name, path)
                except Exception as e:
                    try:
                        os.unlink(outf.name)
                    except:
                        pass
                    raise e

        except IOError as e:
            sys.stderr.write('open() failed: %s\n' % str(e))
        except LookupError as e:
            argparser.error(str(e))

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
