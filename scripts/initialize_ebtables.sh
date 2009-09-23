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

ovpntapintf="tap0"
ovpnvlanintfs="vlan734 vlan735"

# Initializing ebtables could also be done with atomic operations.
ebtables -t filter -F
ebtables -t filter -Z

ebtables -t nat -F
ebtables -t nat -Z

ebtables -t broute -F
ebtables -t broute -Z

ebtables -t filter -P FORWARD DROP
ebtables -t filter -P OUTPUT DROP
ebtables -t filter -P INPUT DROP

# Only allow ARP broadcasts
ebtables -t filter -A FORWARD -i ! ${ovpntapintf} -p ! ARP -d Broadcast -j DROP

for ovpnvlanintf in ${ovpnvlanintfs}
do
    ebtables -t filter -A FORWARD -i ${ovpnvlanintf} -o ${ovpntapintf} -j ACCEPT
done
