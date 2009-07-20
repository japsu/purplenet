#!/bin/bash
export PYTHONPATH=$PWD
export PATH=$PWD/bin:$PATH
export OPENVPN_WEB_DIR=$PWD
export DJANGO_SETTINGS_MODULE=openvpnweb.settings

function manage {
	python $OPENVPN_WEB_DIR/openvpnweb/manage.py $@
}

function hop {
	if [ -x /etc/init.d/httpd ]; then
		sudo service httpd restart
	elif [ -x /etc/init.d/apache2 ]; then
		sudo invoke-rc.d apache2 restart
	else
		sudo apachectl -k restart
	fi
}
