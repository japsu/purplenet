#!/bin/bash
# vim: shiftwidth=4 expandtab
DBUSER=openvpn
DBNAME=openvpn
CADIR=/home/pajukans/Temp/testca
SELINUXENABLED=/usr/sbin/selinuxenabled

set -e
source $(dirname $0)/env.sh

rm -rf "$CADIR"
mkdir -p "$CADIR/copies"

if [ -x $SELINUXENABLED ]; then
    if $SELINUXENABLED; then
        echo "It seems you are running SELinux. Adjusting contexts for CA dir..."
        chcon -R -t httpd_sys_content_rw_t "$CADIR"
    fi
fi

dropdb -U $DBUSER $DBNAME
createdb -U $DBUSER -E UNICODE $DBNAME
python openvpnweb/manage.py syncdb --noinput
#python reinit.py

chmod -R a+rwX "$CADIR"

echo "Restarting Apache with sudo."
if [ -x /etc/init.d/httpd ]; then
    # Fedora
    sudo /etc/init.d/httpd reload
elif [ -x /etc/init/apache2 ]; then
    # Debian
    sudo /etc/init.d/apache2 force-reload
else
    echo "No known init script found for apache. Please restart it yourself."
fi
