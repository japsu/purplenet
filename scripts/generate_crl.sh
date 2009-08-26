#!/bin/sh

ca_name="openvpn-ca-institute-tlt"
crl_file="/etc/ssl/crls/openvpn-ca-institute-tlt.crl"

openssl ca -name $ca_name -gencrl -out $crl_file
