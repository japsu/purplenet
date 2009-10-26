# encoding: utf-8
# vim: shiftwidth=4 expandtab
#
# PurpleNet - a Web User Interface for OpenVPN
# Copyright (C) 2009  Santtu Pajukanta
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Useful helper functions that are used in several places in PurpleNet.
"""

# for python 2.5
from __future__ import with_statement, absolute_import

from django.template.loader import render_to_string
from django.conf import settings
from functools import wraps
from glob import glob

import sys, os
import logging
import zipfile

log = logging.getLogger()

class FileExists(AttributeError):
    pass

def setup_logging(name="DEFAULT", level=logging.INFO, stream=sys.stderr):
    global log
    logging.basicConfig(level=level, stream=stream)
    log = logging.getLogger(name)
    return log

def mkopts(options):
    "mkopts([(short, long, help)]) -> opts, long_opts"

    # Catch a programmer error of conflicting parameter specifications
    for short, long, help in options:
        assert short.endswith(":") == long.endswith("=")

    opts = "".join(short for (short, long, help) in options)
    long_opts = [long for (short, long, help) in options]
    return opts, long_opts

def mkopts_and_usage(headline, options):
    def _usage(stream=sys.stderr):
        return usage(headline, options, stream)

    opts, long_opts = mkopts(options)
    return opts, long_opts, _usage

def usage(headline, options, stream=sys.stderr):
    "usage(headline, [(short, long, help)], stream=sys.stdout)"
    stream.write(headline)
    stream.write("\n\n")
    for short, long, help in options:
        if long is not None:
            stream.write("\t--%s%s" % (
                long,
                "\t" * max(3 - ((len(long) + 2) / 8 + 1), 1)
            ))
        if short is not None:
            stream.write("-%s" % short[0])
        if help is not None:
            stream.write("\t%s\n" % help)

def write_file(filename, contents, force=False, mode=0644):
    if os.path.exists(filename):
        if not os.path.isfile(filename):
            log.error("%s exists and is not a regular file. Will not overwrite (even with force).", filename)
            raise FileExists(filename)

        if force:
            log.debug("%s exists and force set. Overwriting (mode=%o).", filename, mode)
        else:
            log.error("%s exists. Will not overwrite without force.", filename)
            raise FileExists(filename)
    else:
        log.debug("Writing %s (mode=%o)", filename, mode)

    with file(filename, "w") as f:
        f.write(contents)

    os.chmod(filename, mode)

def read_file(filename):
    with open(filename, "r") as f:
        return f.read()

def render_to_file(filename, template_name, context, force):
    write_file(filename, render_to_string(template_name, context), force)

def enum_check(name, arg, allowed):
    if arg not in allowed:
        log.error("%s must be one of %s", name,
            ", ".join(str(i) for i in allowed))
        usage(sys.stderr)
        sys.exit(Exit.COMMAND_LINE_SYNTAX_ERROR)

def mkdir_check(dir, force=False):    
    """mkdir_check(dir, force=False)
    
    Creates the directory specified by dir. If the directory already
    exists, and the Force is not with us, raises an AttributeError.
    """

    if not os.path.exists(dir):
        log.debug("Creating %s", dir)
        os.mkdir(dir)
    else:
        if not os.path.isdir(dir):
            log.error("%s exists and is not a directory. Will" +
                " not overwrite even with force.", dir)
            raise FileExists(dir)

        if force:
            log.debug("%s exists and force set.", dir)
        else:
            log.error("%s exists. Will not overwrite without" +
                " force.", dir)
            raise FileExists(dir)

def coalesce(*args, **kwargs):
    """coalesce(*args, return_none=False) -> one of args or None
    
    Returns the first non-None argument. If all arguments are None, behaviour
    is controlled by return_none: On return_none=True, None is returned. On
    return_none=False, a ValueError is raised.
    """
    for arg in args:
        if arg is not None:
            return arg

    if return_none:
        return None
    else:
        raise ValueError("coalesce with all Nones")

def import_module(module_name):
    """import_module(module_name) -> module
    
    Imports a module by name and returns it. Error behaviour is identical to
    that of __import__, that is, you'll mostly get ImportErrors.
    """
    return __import__(module_name, {}, {}, [''])

def deprecated(func):
    """@deprecated def ...
    
    Tells the reader and user of the code that a function is deprecated.
    A DeprecationWarning is emitted when the wrapped function is called.
    """
    
    @wraps(func)
    def __inner(*args, **kwargs):
        warn(DeprecationWarning("%s is deprecated" % func.__name__))
        return func(*args, **kwargs)
    return __inner

def sanitize_name(name):
    """sanitize_name(name) -> sanitized_name
    
    Sanitizes a name. This means that the name is stripped of non-alphanumeric
    characters and converted to lower case. If the name is reduced to zero
    characters, the bytes seven to ten of the MD5 checksum of the input are
    returned instead.
    """
    # Bytes seven to ten are choosed completely arbitrarily. If someone can
    # think of a better way to handle values that get reduced ad absurdum, go
    # ahead.
    sanitized_name = "".join(i for i in name if i.isalnum()).lower()

    # Django might give us Unicode input.
    if type(sanitized_name) is unicode:
        sanitized_name = sanitized_name.encode("UTF-8")

    if sanitized_name:
        return sanitized_name
    else:
        from md5 import md5
        hasher = md5()
        hasher.update(name)
        return hasher.hexdigest()[12:20]
    
def zip_write_file(zip, filename, contents, mode=0666):
    """zip_write_file(zip, filename, contents, mode=0666)
    
    Writes a file into a ZipFile. Also sets the mode of the file, which
    a plain zip.writestr won't do (resulting in mode=0000).
    """
    
    info = zipfile.ZipInfo(filename)
    info.external_attr = mode << 16L
    zip.writestr(info, contents)

def get_config_templates(config_type="server"):
    # XXX kludge
    templates = set()
    for base in settings.TEMPLATE_DIRS:
        template_files = glob(os.path.join(base, "openvpn_conf/%s/*" % config_type))
        for filename in template_files:
            if filename.startswith(base):
                filename = filename[len(base):]
            if filename.startswith("/"):
                filename = filename[1:]
            templates.add((filename, filename)) 
    return list(templates)
