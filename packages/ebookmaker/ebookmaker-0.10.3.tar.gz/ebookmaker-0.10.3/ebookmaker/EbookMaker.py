#!/usr/bin/env python
#  -*- mode: python; indent-tabs-mode: nil; -*- coding: iso-8859-1 -*-

"""

EbookMaker.py

Copyright 2009-2014 by Marcello Perathoner

Distributable under the GNU General Public License Version 3 or newer.

Stand-alone application to build EPUB and others out of html or rst.

"""

import argparse
import configparser
import collections
import datetime
import hashlib
import logging
import os.path
import re
import sys
import datetime

import six
from six.moves import cPickle

from libgutenberg.GutenbergGlobals import SkipOutputFormat
import libgutenberg.GutenbergGlobals as gg
from libgutenberg.Logger import debug, info, warning, error, exception
from libgutenberg import Logger, DublinCore
from libgutenberg import MediaTypes as mt
from libgutenberg import Cover

from ebookmaker import parsers
from ebookmaker import ParserFactory
from ebookmaker import Spider
from ebookmaker import WriterFactory
from ebookmaker.packagers import PackagerFactory
from ebookmaker import CommonCode
from ebookmaker.CommonCode import Options
from ebookmaker.Version import VERSION

options = Options()

# store paths for system utilities in CONFIG_FILES[0]
# store default command line args in [default_args] section of CONFIG_FILES[1]
CONFIG_FILES = ['/etc/ebookmaker.conf', os.path.expanduser('~/.ebookmaker')]

DEPENDENCIES = collections.OrderedDict((
    ('all', ('html', 'epub', 'kindle', 'pdf', 'txt', 'rst')),
    ('test', ('html', 'epub')),
    ('html', ('html.images', 'html.noimages')),
    ('epub', ('epub.images', 'epub.noimages')),
    ('kindle', ('kindle.images', 'kindle.noimages')),
    ('pdf', ('pdf.images', 'pdf.noimages')),
    ('txt', ('txt.utf-8', 'txt.iso-8859-1', 'txt.us-ascii')),
    ('rst', ('rst.gen', )),
    ('kindle.noimages', ('epub.noimages', )),
    ('kindle.images', ('epub.images', )),
    ('html.noimages', ('picsdir.noimages', )),
    ('html.images', ('picsdir.images', )),
    ('pdf.noimages', ('picsdir.noimages', )),
    ('pdf.images', ('picsdir.images', )),
    ('rst.gen', ('picsdir.images', )),
))

BUILD_ORDER = """
picsdir.images picsdir.noimages
rst.gen
txt.utf-8 txt.iso-8859-1 txt.us-ascii
html.images html.noimages
epub.images epub.noimages
kindle.images kindle.noimages
cover.small cover.medium
pdf.images pdf.noimages
qrcode rdf facebook twitter null""".split()

FILENAMES = {
    'html.noimages': '{id}-noimages-h.html',
    'html.images': '{id}-h.html',

    'epub.noimages': '{id}-epub.epub',
    'epub.images': '{id}-images-epub.epub',

    'kindle.noimages': '{id}-kindle.mobi',
    'kindle.images': '{id}-images-kindle.mobi',

    'pdf.noimages': '{id}-pdf.pdf',
    'pdf.images': '{id}-images-pdf.pdf',

    'txt.utf-8': '{id}-0.txt',
    'txt.iso-8859-1': '{id}-8.txt',
    'txt.us-ascii': '{id}.txt',

    'rst.gen': '{id}-rst.rst',

    'picsdir.noimages': '{id}-noimages.picsdir',  # do we need this ?
    'picsdir.images': '{id}-images.picsdir',  # do we need this ?

    'cover': '{id}-cover.png'
}

COVERPAGE_MIN_AREA = 200 * 200

def make_output_filename(type_, dc):
    """ Make a suitable filename for output type. """

    if dc.project_gutenberg_id:
        # PG book: use PG naming convention
        return FILENAMES[type_].format(id=dc.project_gutenberg_id)
    # not a PG ebook
    return FILENAMES[type_].format(id=gg.string_to_filename(dc.title)[:65])


def elect_coverpage(spider, url):
    """ Find first coverpage candidate that is not too small. """

    coverpage_found = False
    for p in spider.parsers:
        if 'coverpage' in p.attribs.rel:
            if coverpage_found:
                # keep the first one found, reset all others
                p.attribs.rel.remove('coverpage')
                continue
            if hasattr(p, 'get_image_dimen'):
                dimen = p.get_image_dimen()
                if(dimen[0] * dimen[1]) < COVERPAGE_MIN_AREA:
                    p.attribs.rel.remove('coverpage')
                    p_url = p.url if hasattr(p, 'url') else ''
                    warning("removed coverpage candidate %s because too small (%d x %d)" %
                            (p_url, dimen[0], dimen[1]))
                    continue
            coverpage_found = True
    if spider.parsers and not coverpage_found and options.generate_cover:
        if not hasattr(Cover, 'cairo'):
            warning('Cairo not installed, cover generation disabled')
            return
        if options.outputdir:
            dir = options.outputdir
        elif url.startswith('file://'):
            dir = os.path.dirname(os.path.abspath(url[7:]))
        elif url.startswith('file:'):
            dir = os.path.dirname(os.path.abspath(url[5:]))
        else:
            dir = os.path.dirname(os.path.abspath(url))
        debug('generating cover in %s' % dir)
        cover_url = generate_cover(dir)
        if cover_url:
            cover_parser = ParserFactory.ParserFactory.create(cover_url)
            cover_parser.attribs.rel.add('coverpage')
            cover_parser.pre_parse()
            spider.parsers.append(cover_parser)



def generate_cover(dir):
    try:
        cover_image = Cover.draw(options.dc, cover_width=1200, cover_height=1800)
        cover_url = os.path.join(dir, make_output_filename('cover', options.dc))
        with open(cover_url, 'wb+') as cover:
            cover_image.save(cover)
        return cover_url
    except OSError:
        error("OSError, Cairo not installed or couldn't write file.")
        return None

def get_dc(url):
    """ Get DC for book. """

    parser = ParserFactory.ParserFactory.create(url)
    parser.parse()

    # this is needed because the the document is not parsed again
    if options.coverpage_url:
        parser._make_coverpage_link(coverpage_url=options.coverpage_url)


    dc = DublinCore.GutenbergDublinCore()
    try:
        dc.load_from_rstheader(parser.unicode_content())
    except (ValueError, UnicodeError):
        debug("No RST header found.")
        try:
            dc.load_from_parser(parser)
        except (ValueError, AttributeError, UnicodeError):
            debug("No HTML header found.")
            try:
                dc.load_from_pgheader(parser.unicode_content())
            except (ValueError, UnicodeError):
                debug("No PG header found.")

    dc.source = parser.attribs.url
    dc.title = options.title or dc.title or 'NA'

    if options.author:
        dc.add_author(options.author, 'cre')
    if not dc.authors:
        dc.add_author('NA', 'cre')

    dc.project_gutenberg_id = options.ebook or dc.project_gutenberg_id
    if dc.project_gutenberg_id:
        dc.opf_identifier = ('%sebooks/%d' % (gg.PG_URL, dc.project_gutenberg_id))
    else:
        dc.opf_identifier = ('urn:mybooks:%s' %
                             hashlib.md5(dc.source.encode('utf-8')).hexdigest())

    # We need a language to build a valid epub, so just make one up.
    if not dc.languages:
        dc.add_lang_id('en')

    return dc


def add_local_options(ap):
    """ Add local options to commandline. """

    ap.add_argument(
        '--version',
        action='version',
        version="%%(prog)s %s" % VERSION
    )

    ap.add_argument(
        "--make",
        dest="types",
        choices=CommonCode.add_dependencies(['all', 'test'], DEPENDENCIES),
        default=[],
        action='append',
        help="output type (default: all)")

    ap.add_argument(
        "--max-depth",
        metavar="LEVELS",
        dest="max_depth",
        type=int,
        default=1,
        help="go how many levels deep while recursively retrieving pages. "
        "(0 == infinite) (default: %(default)s)")

    ap.add_argument(
        "--strip_links",
        dest="strip_links",
        action="store_true",
        help="strip  <a href='external address' /> links")

    ap.add_argument(
        "--include",
        metavar="GLOB",
        dest="include_urls",
        default=[],
        action="append",
        help="include urls (repeat for more) (default: urls under the same directory)")

    ap.add_argument(
        "--exclude",
        metavar="GLOB",
        dest="exclude_urls",
        default=[],
        action="append",
        help="exclude urls from included urls (repeat for more) (default: none)")

    ap.add_argument(
        "--include-mediatype",
        metavar="GLOB/GLOB",
        dest="include_mediatypes",
        default=mt.TEXT_MEDIATYPES | mt.AUX_MEDIATYPES,
        action="append",
        help="include mediatypes (repeat for more) (eg. 'image/*') "
        "(default: most common text mediatypes)")

    ap.add_argument(
        "--exclude-mediatype",
        metavar="GLOB/GLOB",
        dest="exclude_mediatypes",
        default=[],
        action="append",
        help="exclude this mediatype from included mediatypes "
        "(repeat for more)")

    ap.add_argument(
        "--input-mediatype",
        metavar="MEDIATYPE",
        dest="input_mediatype",
        default=None,
        help="mediatype of input url (default: http response else file extension)")

    ap.add_argument(
        "--mediatype-from-extension",
        dest="mediatype_from_extension",
        action="store_true",
        default=False,
        help="guess all mediatypes from file extension, overrides http response")

    ap.add_argument(
        "--rewrite",
        metavar="from>to",
        dest="rewrite",
        default=[],
        action="append",
        help="rewrite url eg. 'http://www.example.org/>http://www.example.org/index.html'")

    ap.add_argument(
        "--title",
        dest="title",
        default=None,
        help="ebook title (default: from meta)")

    ap.add_argument(
        "--author",
        dest="author",
        default=None,
        help="author (default: from meta)")

    ap.add_argument(
        "--ebook",
        dest="ebook",
        type=int,
        default=0,
        help="ebook no. (default: from meta)")

    ap.add_argument(
        "--output-dir",
        metavar="OUTPUT_DIR",
        dest="outputdir",
        default="./",
        help="output directory (default: ./)")

    ap.add_argument(
        "--output-file",
        metavar="OUTPUT_FILE",
        dest="outputfile",
        default=None,
        help="output file (default: <title>.epub)")

    ap.add_argument(
        "--validate",
        dest="validate",
        action="count",
        help="validate epub through epubcheck")

    ap.add_argument(
        "--section",
        metavar="TAG.CLASS",
        dest="section_tags",
        default=[],
        action="append",
        help="split epub on TAG.CLASS")

    ap.add_argument(
        "--packager",
        dest="packager",
        choices=['ww', 'gzip'],
        default=None,
        help="PG internal use only: which packager to use (default: none)")

    ap.add_argument(
        "--cover",
        dest="coverpage_url",
        default=None,
        help="use the cover specified by an absolute url")

    ap.add_argument(
        "--generate_cover",
        dest="generate_cover",
        action="store_true",
        help="if no cover is specified by the source, or as an argument, generate a cover")

    ap.add_argument(
        "--jobs",
        dest="is_job_queue",
        action="store_true",
        help="PG internal use only: read pickled job queue from stdin")

    ap.add_argument(
        "--extension-package",
        metavar="PYTHON_PACKAGE",
        dest="extension_packages",
        default=[],
        action="append",
        help="PG internal use only: load extensions from package")

    ap.add_argument(
        "url",
        help="url of file to convert")


def open_log(path):
    """ Open a logfile in the output directory. """

    handler = logging.FileHandler(path, "a")
    handler.setFormatter(Logger.CustomFormatter(Logger.LOGFORMAT))
    handler.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(handler)
    return handler


def close_log(handler):
    """ Close logfile handler. """

    logging.getLogger().removeHandler(handler)
    handler.close()


def do_job(job):
    """ Do one job. """

    log_handler = None
    Logger.ebook = job.ebook
    if job.logfile:
        log_handler = open_log(os.path.join(os.path.abspath(job.outputdir), job.logfile))

    debug('=== Building %s ===' % job.type)
    start_time = datetime.datetime.now()
    try:
        if job.url:
            spider = Spider.Spider()
            dirpath = os.path.dirname(job.url)  # platform native path
            spider.include_urls += (options.include_urls or
                                    [parsers.webify_url(dirpath) + '/*']) # use for parser only

            spider.include_mediatypes += options.include_mediatypes
            if job.subtype == '.images' or job.type == 'rst.gen':
                spider.include_mediatypes.append('image/*')

            spider.exclude_urls += options.exclude_urls

            spider.exclude_mediatypes += options.exclude_mediatypes

            spider.max_depth = options.max_depth or six.MAXSIZE

            for rewrite in options.rewrite:
                from_url, to_url = rewrite.split('>')
                spider.add_redirection(from_url, to_url)

            attribs = parsers.ParserAttributes()
            attribs.url = parsers.webify_url(job.url)
            attribs.id = 'start'

            if options.input_mediatype:
                attribs.orig_mediatype = attribs.HeaderElement.from_str(
                    options.input_mediatype)

            spider.recursive_parse(attribs)
            elect_coverpage(spider, job.url)
            job.url = spider.redirect(job.url)
            job.base_url = job.url
            job.spider = spider

        writer = WriterFactory.create(job.maintype)
        writer.build(job)

        if options.validate:
            writer.validate(job)

        packager = PackagerFactory.create(options.packager, job.type)
        if packager:
            packager.package(job)

        if job.type == 'html.images':
            # FIXME: hack for push packager
            options.html_images_list = list(job.spider.aux_file_iter())

    except SkipOutputFormat as what:
        warning("%s" % what)

    except Exception as what:
        exception("%s" % what)

    end_time = datetime.datetime.now()
    info(' %s made in %s' % (job.type, end_time - start_time))

    if log_handler:
        close_log(log_handler)
        log_handler = None


def config():
    """ Process config files and commandline params. """

    ap = argparse.ArgumentParser(prog='EbookMaker')
    CommonCode.add_common_options(ap, CONFIG_FILES[1])
    add_local_options(ap)
    CommonCode.set_arg_defaults(ap, CONFIG_FILES[1])

    global options
    options.update(vars(CommonCode.parse_config_and_args(
        ap,
        CONFIG_FILES[0],
        {
            'proxies' : None,
            'xelatex' : 'xelatex',
            'mobigen' : 'kindlegen',
            'mobilang': '',
            'groff'   : 'groff',
            'rhyming_dict': None,
            'timestamp': datetime.datetime.today().isoformat()[:19],
        }
    )))

    if not re.search(r'^(https?|file):', options.url):
        options.url = os.path.abspath(options.url)


def main():
    """ Main program. """

    try:
        config()
    except configparser.Error as what:
        error("Error in configuration file: %s", str(what))
        return 1

    Logger.set_log_level(options.verbose)

    options.types = options.types or ['all']
    options.types = CommonCode.add_dependencies(options.types, DEPENDENCIES, BUILD_ORDER)
    debug("Building types: %s" % ' '.join(options.types))
    start_time = datetime.datetime.now()

    ParserFactory.load_parsers()
    WriterFactory.load_writers()
    PackagerFactory.load_packagers()

    if options.is_job_queue:
        job_queue = cPickle.load(sys.stdin.buffer) # read bytes
    else:
        options.dc = get_dc(options.url) # this is when doc at url gets parsed!
        job_queue = []
        output_files = dict()
        for type_ in options.types:
            job = CommonCode.Job(type_)
            job.url = options.url
            job.ebook = options.ebook
            job.dc = options.dc
            job.outputdir = options.outputdir
            job.outputfile = options.outputfile or make_output_filename(type_, options.dc)
            output_files[type_] = job.outputfile
            absoutputdir = os.path.abspath(job.outputdir)
            if job.type == 'kindle.images':
                job.url = os.path.join(absoutputdir, output_files['epub.images'])
            elif job.type == 'kindle.noimages':
                job.url = os.path.join(absoutputdir, output_files['epub.noimages'])

            job_queue.append(job)

    for j in job_queue:
        options.dc = j.dc
        options.outputdir = j.outputdir
        do_job(j)

    packager = PackagerFactory.create(options.packager, 'push')
    if packager:
        # HACK: the WWers ever only convert one ebook at a time
        job = job_queue[0]
        job.outputfile = '%d-final.zip' % (options.dc.project_gutenberg_id)
        packager.package(job)

    end_time = datetime.datetime.now()
    info(' Finished jobs. Total time: %s' % (end_time - start_time))
    return 0


if __name__ == "__main__":
    sys.exit(main())
