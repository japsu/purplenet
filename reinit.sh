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

echo "Please do not run this script in a production environment."
echo "To confirm you have read and understood this warning, please edit the"
echo "script and comment the 'exit 1' at line 26 out."
exit 1

DBUSER=openvpn
DBNAME=openvpn
CADIR=/home/pajukans/Temp/testca
SELINUXENABLED=/usr/sbin/selinuxenabled

set -e
source $(dirname $0)/env.sh

if [ -d "$CADIR" ]; then
        echo "Nuking the CA dir with sudo (it prolly has files owned by the web server"
        sudo rm -rf "$CADIR"
fi

mkdir -p "$CADIR"
chmod a+rwx "$CADIR"

if [ -x $SELINUXENABLED ]; then
    if $SELINUXENABLED; then
        echo "It seems you are running SELinux. Adjusting contexts for CA dir..."
        chcon -R -t httpd_sys_content_rw_t "$CADIR"
    fi
fi

dropdb -U $DBUSER $DBNAME
createdb -U $DBUSER -E UNICODE $DBNAME
python openvpnweb/manage.py syncdb --noinput

echo "Restarting Apache with sudo."
if [ -x /etc/init.d/httpd ]; then
    # Fedora
    sudo /etc/init.d/httpd reload
elif [ -x /etc/init.d/apache2 ]; then
    # Debian
    sudo /etc/init.d/apache2 force-reload
else
    echo "No known init script found for apache. Please restart it yourself."
fi

#python bin/reinit_hard.py
#python bin/reinit_soft.py
