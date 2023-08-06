#!/usr/bin/env python
#  -*- mode: python; indent-tabs-mode: nil; -*- coding: iso-8859-1 -*-

"""
CommonCode.py

Copyright 2014 by Marcello Perathoner

Distributable under the GNU General Public License Version 3 or newer.

Common code for EbookMaker and EbookConverter.

"""

import os.path

from six.moves import configparser

from libgutenberg.CommonOptions import Options

class Struct (object):
    pass

options = Options()

class Job (object):
    """Hold 'globals' for a job.

    A job is defined as one unit of work, acting on one input url.

    """

    def __init__ (self, type_):
        self.type = type_
        self.maintype, self.subtype = os.path.splitext (self.type)

        self.url = None
        self.outputdir = None
        self.outputfile = None
        self.logfile = None
        self.dc = None


    def __str__ (self):
        l = []
        for k, v in self.__dict__.items ():
            l.append ("%s: %s" % (k, v))
        return '\n'.join (l)


def add_dependencies (targets, deps, order = None):
    """ Add dependent formats and optionally put into right build order. """

    for target, deps in deps.items ():
        if target in targets:
            targets = list(set(targets).union(deps))
    if order:
        return list (filter (targets.__contains__, order))
    return targets


def add_common_options (ap, user_config_file):
    """ Add aptions common to all programs. """

    ap.add_argument (
        "--verbose", "-v",
        action   = "count",
        default  = 0,
        help     = "be verbose (-v -v be more verbose)")

    ap.add_argument (
        "--config",
        metavar  = "CONFIG_FILE",
        dest     = "config_file",
        action   = "append",
        default  = user_config_file,
        help     = "read config file (default: %(default)s)")

def set_arg_defaults(ap, config_file):
    # get default command-line args
    cp = configparser.ConfigParser ()
    cp.read (config_file)
    if cp.has_section('DEFAULT_ARGS'):
        ap.set_defaults(**dict(cp.items('DEFAULT_ARGS')))

def parse_config_and_args (ap, sys_config, defaults = None):

    # put command-line args into options
    options.update(vars(ap.parse_args ()))

    cp = configparser.ConfigParser ()
    cp.read ((sys_config, options.config_file))

    options.config = Struct ()

    for name, value in defaults.items ():
        setattr (options.config, name.upper (), value)

    for section in cp.sections ():
        for name, value in cp.items (section):
            setattr (options.config, name.upper (), value)

    return options
