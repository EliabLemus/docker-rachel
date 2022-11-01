#!/bin/sh
set -e

# first arg is `-f` or `--some-option`
if [ "${1#-}" != "$1" ]; then
	set -- php "$@"
fi
#instala los modulos que se encuentren en el volumen en tmp

service kolibri start &
/usr/bin/python3 /var/kiwix/bin/rachel_kiwix.py --start
/usr/bin/python3 /var/install_modules/bin/install_modules.py &
sudo ln -sf /proc/$$/fd/1 /var/log/apache2/access.log
sudo ln -sf /proc/$$/fd/2 /var/log/apache2/error.log

exec "$@"