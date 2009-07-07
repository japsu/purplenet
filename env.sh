#!/bin/bash
export PYTHONPATH=$PWD
export PATH=$PWD/bin:$PATH
export OPENVPN_WEB_DIR=$PWD

function manage {
	python $OPENVPN_WEB_DIR/openvpnweb/manage.py $@
}
