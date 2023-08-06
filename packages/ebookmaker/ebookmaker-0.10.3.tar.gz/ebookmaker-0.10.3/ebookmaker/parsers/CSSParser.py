#!/usr/bin/env python
#  -*- mode: python; indent-tabs-mode: nil; -*- coding: iso-8859-1 -*-

"""

CSSParser.py

Copyright 2009 by Marcello Perathoner

Distributable under the GNU General Public License Version 3 or newer.

Open an url and return raw data.

"""

import re
from six.moves import urllib
import logging

import cssutils

from libgutenberg.Logger import debug
from libgutenberg.MediaTypes import mediatypes as mt

from ebookmaker import parsers
from ebookmaker.parsers import ParserBase

RE_ELEMENT = re.compile (r'((?:^|\s)[a-z0-9]+)', re.I)

mediatypes = (mt.css, )

class Parser (ParserBase):
    """ Parse an external CSS file. """

    def __init__ (self, attribs = None):
        cssutils.log.setLog (logging.getLogger ('cssutils'))
        # logging.DEBUG is way too verbose
        cssutils.log.setLevel (max (cssutils.log.getEffectiveLevel (), logging.INFO))
        ParserBase.__init__ (self, attribs)
        self.sheet = None


    def parse (self):
        """ Parse the CSS file. """

        if self.sheet is not None:
            return

        parser = cssutils.CSSParser ()
        if self.fp:
            self.sheet = parser.parseString (self.unicode_content())
        else:
            try:
                self.sheet = parser.parseUrl (self.attribs.url)
            except ValueError:
                logging.error ('Missing file: %s' % self.attribs.url)
                return
            
        self.attribs.mediatype = parsers.ParserAttributes.HeaderElement ('text/css')
        self.unpack_media_handheld (self.sheet)
        self.lowercase_selectors (self.sheet)


    def parse_string (self, s):
        """ Parse the CSS in string. """

        if self.sheet is not None:
            return

        parser = cssutils.CSSParser ()
        self.sheet = parser.parseString (s)

        self.attribs.mediatype = parsers.ParserAttributes.HeaderElement ('text/css')
        self.unpack_media_handheld (self.sheet)
        self.lowercase_selectors (self.sheet)


    @staticmethod
    def iter_properties (sheet):
        """ Iterate on properties in css. """
        for rule in sheet:
            if rule.type == rule.STYLE_RULE:
                for prop in rule.style:
                    yield prop


    @staticmethod
    def unpack_media_handheld (sheet):
        """ unpack a @media handheld rule """
        for rule in sheet:
            if rule.type == rule.MEDIA_RULE:
                if rule.media.mediaText.find ('handheld') > -1:
                    debug ("Unpacking CSS @media handheld rule.")
                    rule.media.mediaText = 'all'
                    rule.insertRule (cssutils.css.CSSComment ('/* was @media handheld */'), 0)


    @staticmethod
    def lowercase_selectors (sheet):
        """ make selectors lowercase to match xhtml tags """
        for rule in sheet:
            if rule.type == rule.STYLE_RULE:
                for sel in rule.selectorList:
                    sel.selectorText = RE_ELEMENT.sub (lambda m: m.group(1).lower (),
                                                       sel.selectorText)


    def rewrite_links (self, f):
        """ Rewrite all links using the function f. """
        cssutils.replaceUrls (self.sheet, f)


    def get_image_urls (self):
        """ Return the urls of all images in document.

        Images are graphic files. The user may choose if he wants
        images included or not.

        """

        images = []

        for prop in self.iter_properties (self.sheet):
            if (prop.value.cssValueType == prop.value.CSS_PRIMITIVE_VALUE and
                prop.value.primitiveType == prop.value.CSS_URI):
                url = urllib.parse.urljoin (self.attribs.url, prop.value.cssText)
                images.append (url)

        return  images


    def get_aux_urls (self):
        """ Return the urls of all auxiliary files in document.

        Auxiliary files are non-document files you need to correctly
        display the document file, eg. CSS files.

        """

        aux = []

        for rule in self.sheet:
            if rule.type == rule.IMPORT_RULE:
                aux.append (urllib.parse.urljoin (self.attribs.url, rule.href))

        return  aux


    def serialize (self):
        """ Serialize CSS. """

        return self.sheet.cssText
