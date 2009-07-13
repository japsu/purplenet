#!/bin/bash
# vim: shiftwidth=4 expandtab
DBUSER=openvpn
DBNAME=openvpn

set -e
source $(dirname $0)/env.sh

dropdb -U $DBUSER $DBNAME
createdb -U $DBUSER -E UNICODE $DBNAME
python openvpnweb/manage.py syncdb --noinput
python reinit.py

echo "Restarting Apache with sudo."
if [ -x /etc/init.d/httpd ]; then
    # Fedora
    sudo /etc/init.d/httpd restart
elif [ -x /etc/init/apache2 ]; then
    # Debian
    sudo /etc/init.d/apache2 force-reload
else
    echo "No known init script found for apache. Please restart it yourself."
fi
