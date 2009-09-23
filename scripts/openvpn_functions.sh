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

# Include the configuration file
. openvpn_verkko.conf

# Define isset function.
isset() {
    if eval [ -z "\$$1" ]; then
	echo "Error: In a script $0, the variable \$$1 is not set or is empty. Execution aborted."
	
	exit 1
    fi
}

# Check that at least necessary programs are defined.
isset ip
isset vconfig
isset brctl
isset iptables
isset ebtables

tolower() {
    local char="$*"

    out=$(echo $char | tr [:upper:] [:lower:])

    unset out
    unset char
    return $out
}

check_func_params() {
    func="$1"
    shift
    pos=1

    for param in "$@"
    do
      if [ -z "$param" ]; then
	  echo "Error: The parameter no. $pos of function '$func' was empty in a script $0."

	  exit 1
      fi

      let "pos+=1"
    done
}

if [ ${openvpn_debug_dry_run:-"FALSE"} != "FALSE" ]; then
    openvpn_debug="TRUE"
fi

debug_msg() {
    if [ ${openvpn_debug:-"FALSE"} != "FALSE" ]; then
	echo ""
	echo "============================================================"
	echo "DEBUG: $0"
	echo "============================================================"
	echo $*
	echo ""
    fi
}

run_cmd() {
    debug_msg "Running command: " "$*"

    if [ ${openvpn_debug_dry_run:-"FALSE"} != "FALSE" ]; then
	echo "Dry run. The command was not executed."
    else
	"$*"
    fi
}

run_cmd_list() {
    for cmd in "$@"
    do
      run_cmd "$cmd"
    done
}

generate_fwmark() {
    # Generate a 32-bit value
    let "return_value = `head -c16 /dev/urandom | md5sum | tr -d [a-z] | cut -d' ' -f1` % 4294967295"

    return $return_value
}

interface_up() {
    is_param_defined "interface_up" "$1"

    run_cmd "$ip" link set "$1" up
}

interface_down() {
    is_param_defined('interface_down', "$1")

    run_cmd "$ip" link set "$1" down
}

create_vlan_interfaces() {
    run_cmd $vconfig set_name_type VLAN_PLUS_VID_NO_PAD

    for interface in ${interfaces_out[@]}
    do
      eval for vlan in \${vlans_${interface}[@]}\; \
	   do \
	     run_cmd $vconfig add $interface \$vlan; \
	     run_cmd $ip link set vlan\${vlan} up; \
	   done
    done
}

remove_vlan_interfaces() {
    for interface in ${interfaces_out[@]}
    do
      eval for vlan in \${vlans_${interface}[@]}\; \
	   do \
	     run_cmd $vconfig rem \$vlan; \
	   done
    done

    #run_cmd $vconfig set_name_type DEV_PLUS_VID_NO_PAD
}

vconfig_modify_interfaces() {
    for interface in ${interfaces_out[@]}
    do
      eval for vlan in \${vlans_${interface}[@]}\; \
	   do \
	     run_cmd_list "$@"; \
	   done
    done
}

create_bridge() {
    isset bridge_name

    remove_bridge

    run_cmd $brctl addbr $bridge_name

    # setageingtime, setgcint
    # BPDU dst mac 01:80:c2:00:00:00
    run_cmd $brctl stp $bridge_name on
    run_cmd $brctl setbridgeprio $bridge_name 65535
    run_cmd $brctl setfd $bridge_name 15
}

remove_bridge() {
    isset bridge_name

    run_cmd $ip link set $bridge_name down



    run_cmd $brctl delbr $bridge_name
}

add_interface_to_bridge() {
    brctl_modify_interface addif
}

remove_interface_from_bridge() {
    brct_modify_interface delif
}

brctl_modify_interface() {
    isset interfaces_openvpn
    isset interfaces_out

    for interface in $interfaces_openvpn
    do
      run_cmd $brctl $action $bridge_name $interface
    done

    for interface in $interfaces_out
    do
      run_cmd $brctl $action $bridge_name $interface
    done
}

initialize_fw() {
    run_cmd $1 -t filter -F
    run_cmd $1 -t filter -Z
    run_cmd $1 -t filter -P FORWARD DENY
}

initialize_iptables() {
    initialize_fw $iptables
}

initialize_ebtables() {
    initialize_fw $ebtables
}
