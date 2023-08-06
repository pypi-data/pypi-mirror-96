#!/usr/bin/env python
#  -*- mode: python; indent-tabs-mode: nil; -*- coding: iso-8859-1 -*-

"""

Spider.py

Copyright 2009 by Marcello Perathoner

Distributable under the GNU General Public License Version 3 or newer.

Rudimentary Web Spider

"""


import fnmatch

from six.moves import urllib

import libgutenberg.GutenbergGlobals as gg
from libgutenberg.GutenbergGlobals import NS
from libgutenberg.Logger import debug, warning, error
from libgutenberg import MediaTypes

from ebookmaker import parsers
from ebookmaker.ParserFactory import ParserFactory


class Spider(object):
    """ A very rudimentary web spider. """

    def __init__(self):
        self.parsed_urls = set()
        self.parsers = []
        self.redirection_map = {}

        self.include_urls = []
        self.exclude_urls = []
        self.include_mediatypes = []
        self.exclude_mediatypes = []
        self.max_depth = 1


    def recursive_parse(self, root_attribs):
        """ Do a recursive parse starting from url.

        Do a breadth-first traversal. Assuming the first page contains
        a linked TOC, this will get us a more natural ordering of the
        pages than a depth-first traversal.

        """

        queue = []

        debug("Start of retrieval")

        # enqueue root url

        self.enqueue(queue, 0, root_attribs, True)

        while queue:
            depth, attribs = queue.pop(0)

            url = self.redirect(attribs.url)
            if url in self.parsed_urls:
                continue

            parser = ParserFactory.create(url, attribs)

            # Maybe the url was redirected to something we already have?
            url = parser.attribs.url
            if url in self.parsed_urls:
                continue
            self.parsed_urls.add(url)

            self.add_redirection(parser.attribs.orig_url, url)
            parser.pre_parse()
            self.parsers.append(parser)

            # look for more documents to add to the queue
            debug("Requesting iterlinks for: %s ..." % url)
            for url, elem in parser.iterlinks():
                url = urllib.parse.urldefrag(url)[0]
                if url == parser.attribs.url or url in self.parsed_urls:
                    continue
                if elem.get('rel') == 'nofollow':
                    # remove link to content not followed
                    elem.tag = 'span'
                    elem.set('data-nofolllow-href', elem.get('href'))
                    del elem.attrib['href']
                    del elem.attrib['rel']
                    warning('not followed: %s' % url)
                    continue

                new_attribs = parsers.ParserAttributes()
                new_attribs.url = url
                new_attribs.referrer = parser.attribs.url

                for k, v in elem.items():
                    if k in ('id', 'title'):
                        setattr(new_attribs, k, v)
                    elif k == 'type':
                        new_attribs.orig_mediatype = new_attribs.HeaderElement.from_str(v)
                    elif k == 'rel':
                        new_attribs.rel.update(v.lower().split())

                tag = elem.tag
                if tag == NS.xhtml.a:
                    if self.is_image(new_attribs) and self.is_included_url(new_attribs) and \
                            self.is_included_mediatype(new_attribs):
                        # need to wrap an image
                        wrapper_parser = parsers.WrapperParser.Parser(new_attribs)
                        if wrapper_parser.attribs.url not in self.parsed_urls:
                            ParserFactory.parsers[wrapper_parser.attribs.url] = wrapper_parser
                            self.parsers.append(wrapper_parser)
                            self.parsed_urls.add(wrapper_parser.attribs.url)
                        elem.set('href', wrapper_parser.attribs.url)
                        new_attribs.referrer = wrapper_parser.attribs.url
                        elem.set('title', wrapper_parser.attribs.title)
                        self.enqueue(queue, depth + 1, new_attribs, False)
                    else:
                        self.enqueue(queue, depth + 1, new_attribs, True)
                        
                elif tag == NS.xhtml.img:
                    self.enqueue(queue, depth, new_attribs, False)
                elif tag == NS.xhtml.link:
                    if new_attribs.rel.intersection(('stylesheet', 'coverpage')):
                        self.enqueue(queue, depth, new_attribs, False)
                    else:
                        self.enqueue(queue, depth + 1, new_attribs, True)
                elif tag == NS.xhtml.object:
                    self.enqueue(queue, depth, new_attribs, False)

        debug("End of retrieval")

        # rewrite redirected urls
        if self.redirection_map:
            for parser in self.parsers:
                parser.remap_links(self.redirection_map)

        self.topological_sort()


    def enqueue(self, queue, depth, attribs, is_doc):
        """ Enqueue url for parsing."""
        if is_doc:
            if not self.is_included_url(attribs):
                warning('External link in %s: %s' % (attribs.referrer, attribs.url))
                return
            if depth >= self.max_depth:
                error('Omitted file %s due to depth > max_depth' % attribs.url)
                return
        if not self.is_included_mediatype(attribs) and not self.is_included_relation(attribs):
            return
        elif not self.is_included_url(attribs) and not self.is_included_relation(attribs):
            error('Failed for embedded media in %s from disallowed location: %s'
                  % (attribs.referrer, attribs.url))
            return

        queue.append((depth, attribs))


    def is_image(self, attribs):
        """ Return True if png, gif, svg or jpg. """
        return self.get_mediatype(attribs) in parsers.ImageParser.mediatypes


    def is_included_url(self, attribs):
        """ Return True if this document is eligible. """

        url = attribs.url

        included = any([fnmatch.fnmatchcase(url, x) for x in self.include_urls])
        excluded = any([fnmatch.fnmatchcase(url, x) for x in self.exclude_urls])

        if included and not excluded:
            return True

        if excluded:
            debug("Dropping excluded %s" % url)
        if not included:
            debug("Dropping not included %s" % url)
        return False


    def get_mediatype(self, attribs):
        """ Get mediatype out of attribs, guessing if needed. """
        if attribs.orig_mediatype is None:
            mediatype = MediaTypes.guess_type(attribs.url)
            if mediatype:
                attribs.orig_mediatype = attribs.HeaderElement(mediatype)
            else:
                return None
        return attribs.orig_mediatype.value


    def is_included_mediatype(self, attribs):
        """ Return True if this document is eligible. """

        mediatype = self.get_mediatype(attribs)
        if not mediatype:
            warning('Mediatype could not be determined from url %s' % attribs.url)
            return True # always include if mediatype unknown

        included = any([fnmatch.fnmatch(mediatype, pattern)
                        for pattern in self.include_mediatypes])
        excluded = any([fnmatch.fnmatch(mediatype, pattern)
                        for pattern in self.exclude_mediatypes])

        if included and not excluded:
            return True

        if excluded:
            debug("Dropping excluded mediatype %s" % mediatype)
        if not included:
            debug("Dropping not included mediatype %s" % mediatype)

        return False


    def is_included_relation(self, attribs):
        """ Return True if this document is eligible. """

        keep = attribs.rel.intersection(('coverpage', 'important', 'linked_image'))
        if keep:
            debug("Not dropping after all because of rel.")

        return keep


    def topological_sort(self):
        """ Do a topological sort of documents using <link rel='next'> """

        relnext = [(p.attribs.referrer, p.attribs.url)
                   for p in self.parsers if 'next' in p.attribs.rel]
        if relnext:
            try:
                d = {}
                for order, url in enumerate(gg.topological_sort(relnext)):
                    d[url] = order
                    debug("%s order %d" % (url, order))
                for parser in self.parsers:
                    parser.order = d.get(parser.attribs.url, 999999)
                self.parsers.sort(key=lambda p: p.order)

            except Exception:
                pass


    def add_redirection(self, from_url, to_url):
        """ Remember this redirection. """

        if from_url != to_url:
            self.redirection_map[from_url] = to_url
            debug("Adding redirection from %s to %s" % (from_url, to_url))


    def redirect(self, url):
        """
        Redirect url.

        Parsers are cached under the 200 url. This is an offline redirect
        to find the 200 url.

        """
        return self.redirection_map.get(url, url)


    def dict_urls_mediatypes(self):
        """ Return a dict of all parsed urls and mediatypes. """
        return dict([(p.attribs.url, p.mediatype()) for p in self.parsers])


    def aux_file_iter(self):
        """ Iterate over image files. Return absolute urls. """

        for p in self.parsers:
            if hasattr(p, 'resize_image'):
                yield p.attribs.url
