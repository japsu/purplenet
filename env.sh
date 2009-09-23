#!/bin/bash
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

export PYTHONPATH=$PWD
export PATH=$PWD/bin:$PATH
export OPENVPN_WEB_DIR=$PWD
export DJANGO_SETTINGS_MODULE=openvpnweb.settings

function manage {
	python $OPENVPN_WEB_DIR/openvpnweb/manage.py $@
}

function hop {
	if [ -x /etc/init.d/httpd ]; then
		sudo service httpd restart
	elif [ -x /etc/init.d/apache2 ]; then
		sudo invoke-rc.d apache2 restart
	else
		sudo apachectl -k restart
	fi
}
