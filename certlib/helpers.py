#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# OpenSSL Certificate Authority generation script
# Department of Communications Engineering, 
# Tampere University of Technology (TUT)
#
# Copyright (c) 2009 Santtu Pajukanta
# Copyright (c) 2008, 2009 Tuure Vartiainen, Antti Niemelä, Vesa Salo
# 
# 

# for python 2.5
from __future__ import with_statement, absolute_import

from django.template.loader import render_to_string

import sys, os
import logging

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
	opts = "".join(short for (short, long, help) in options)
	long_opts = [long for (short, long, help) in options]
	return opts, long_opts

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

