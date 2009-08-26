#!/bin/sh

vde_switch -sock /tmp/vde.ctl -mgmt /tmp/vde.mgmt -daemon

vde_plug2tap -sock /tmp/vde.ctl -daemon tap1
vde_plug2tap -sock /tmp/vde.ctl -daemon tap2
vde_plug2tap -sock /tmp/vde.ctl -daemon tap3

# unixterm /tmp/vde.mgmt
