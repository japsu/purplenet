#!/bin/sh

brctl delbr ovpn

ifconfig tap0 up
ifconfig tap1 up

brctl addbr ovpn
brctl addif ovpn tap0
brctl addif ovpn tap1
