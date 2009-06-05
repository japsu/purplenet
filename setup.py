#!/usr/bin/env python
from distutils.core import setup
setup(
	name="OpenVPNweb",
	version="0.0",
	packages=[
		"certlib",
		"openvpnweb",
		"openvpnweb.openvpn_userinterface"
	],
	data_files=[
		("share/openvpn-web/media", "media/*"),
		("share/openvpn-web/templates", "templates/*")
	]
)
