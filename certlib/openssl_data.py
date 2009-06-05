# -*- coding: utf-8 -*-
#
# OpenSSL Certificate Authority generation script
# Department of Communications Engineering, 
# Tampere University of Technology (TUT)
#
# Copyright (c) 2009 Santtu Pajukanta
# 
# 

from __future__ import absolute_import

from .enums import CAType

base = dict(
	default_days = 365,
	default_crl_days = 30,
	basic_constraints = "critical,CA:false",
	key_usage = "critical,digitalSignature,keyEncipherment"
)

ca = dict(base,
	default_days = 3650,
	basic_constraints = "CA:true",
	key_usage = "critical,cRLSign,keyCertSign"
)

server = dict(base,
	extended_key_usage = "critical,serverAuth"
)

client = dict(base,
	extended_key_usage = "critical,clientAuth"
)

config_data = {
	CAType.CA : ca,
	CAType.SERVER : server,
	CAType.CLIENT : client
}

