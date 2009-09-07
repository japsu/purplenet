#!/bin/sh

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
