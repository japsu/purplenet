#!/bin/sh

#
# OpenVPN Proof of Concept Implementation Project, 
# TLT-1600 Design Project in Telecommunications, 
# Department of Communications Engineering, 
# Tampere University of Technology (TUT)
#
# Copyright (c) 2008, 2009 Tuure Vartiainen
# 
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#

# action address vlan
# e.g. add 00:11:22:33:44:55 20

in_intf="tap0"
out_intf_suffix="vlan"

# either "add" or "delete"
action=$1
mac_address=$2

add_rule() {
    mac_address=$1
    vlan=$2

    ebtables -t filter -A FORWARD -i $in_intf -s $mac_address -o ${out_intf_suffix}${vlan} -j ACCEPT &> /dev/null
}

delete_rule() {
    mac_address=$1
    out_intf=`ebtables -L --Lmac2|grep "$mac_address"|awk '{ print $6; }'`


    if [ ! -z "$out_intf" ]; then
        ebtables -t filter -D FORWARD -i $in_intf -s $mac_address -o $out_intf -j ACCEPT &> /dev/null
    fi
}

if [ "$action" = "add" ]; then
    vlan=$3

    delete_rule $mac_address
    add_rule $mac_address $vlan
elif [ "$action" = "delete" ]; then
    delete_rule $mac_address
fi

exit 0
