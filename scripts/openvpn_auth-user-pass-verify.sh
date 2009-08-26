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
