#!/bin/sh
set -e

# first arg is `-f` or `--some-option`
if [ "${1#-}" != "$1" ]; then
	set -- php "$@"
fi

service kiwix start 
exec "$@"
# #!/bin/sh

# # Download if necessary a file
# if [ ! -z "$DOWNLOAD" ]
# then
#     ZIM=`basename $DOWNLOAD`
#     wget $DOWNLOAD -O "$ZIM"

#     # Set arguments
#     if [ "$#" -eq "0" ]
#     then
#         set -- "$@" $ZIM
#     fi
# fi

# # CMD="/var/kiwix/bin/kiwix-serve --verbose --port=81 --library $@"
# # CMD="/var/kiwix/bin/kiwix-serve --version"
# echo $CMD
# $CMD

# # If error, print the content of /data
# if [ $? -ne 0 ]
# then
#     echo "Here is the content of /data:"
#     find /data -type f
# fi
# # #!/bin/bash

# # exec python3 /var/kiwix/bin/rachel_kiwix.py --start
# # # exec /var/kiwix/bin/kiwix-serve --port=81 --attachToProcess=1

# # exec "$@"