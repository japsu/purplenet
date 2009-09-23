#!/bin/sh
# encoding: utf-8
# vim: shiftwidth=4 expandtab
#
# PurpleNet - a Web User Interface for OpenVPN
# Copyright (C) 2008, 2009  Tuure Vartiainen
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

. openvpn_functions.sh

isset interfaces_openvpn
isset interfaces_out

run_cmd $iptables -t filter -F
run_cmd $iptables -t filter -Z
run_cmd $iptables -t filter -P FORWARD DENY

for openvpn_in_dev in $interfaces_openvpn
do
    for openvpn_out_dev in $interfaces_out
    do
        run_cmd $iptables -t filter -A FORWARD -i ${openvpn_in_dev} -o ${openvpn_out_dev} -j ACCEPT
    done
done
