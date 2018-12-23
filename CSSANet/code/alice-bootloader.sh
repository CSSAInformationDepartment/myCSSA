#!/bin/sh

>&2 echo '###############################################################################'
>&2 echo '#                    Desinged & Managed by Josh.Le.LU                         #'
>&2 echo '#                                                                             #'
>&2 echo '#                     █████╗ ██╗     ██╗ ██████╗███████╗                      #'
>&2 echo '#                    ██╔══██╗██║     ██║██╔════╝██╔════╝                      #'
>&2 echo '#                    ███████║██║     ██║██║     █████╗                        #'
>&2 echo '#                    ██╔══██║██║     ██║██║     ██╔══╝                        #'
>&2 echo '#                    ██║  ██║███████╗██║╚██████╗███████╗                      #'
>&2 echo '#                    ╚═╝  ╚═╝╚══════╝╚═╝ ╚═════╝╚══════╝                      #'
>&2 echo '#          ______             _   _                     _                     #'
>&2 echo '#          | ___ \           | | | |                   | |                    #'
>&2 echo '#          | |_/ / ___   ___ | |_| |     ___   __ _  __| | ___ _ __           #'
>&2 echo '#          | ___ \/ _ \ / _ \| __| |    / _ \ / _` |/ _` |/ _ \  __|          #'
>&2 echo '#          | |_/ / (_) | (_) | |_| |___| (_) | (_| | (_| |  __/ |             #'    
>&2 echo '#          \____/ \___/ \___/ \__\_____/\___/ \__,_|\__,_|\___|_|             #'
>&2 echo '#                                                                             #'
>&2 echo '#                                                                             #'
>&2 echo '#                Proprietary version made for myCSSA project                  #'
>&2 echo '#                             Version: 1.1b(C)                                #'
>&2 echo '#                                                                             #'
>&2 echo '###############################################################################'
sleep 1

TIMEOUT=15
QUIET=0

SQLCONNECTED='FALSE'

>&2 echo 'Checking Postgres'

until [ $SQLCONNECTED = 'TRUE' ] 
do
    SERVER=db
    PORT=5432
    `nc -z $SERVER $PORT`
    result1=$?
    if [  "$result1" != 0 ]; then
      >&2 echo 'Postgres is unavailable - Waiting for 3 sec to Retry'
      sleep 3
    else
        >&2 echo "Postgres is up - Web Service Engine boot sequence initiated"
        SQLCONNECTED='TRUE'
    fi
done

python3 manage.py makemigrations || ( echo '[Bootloader] Migration Check Failure!'; exit 1);

python3 manage.py migrate || ( echo '[Bootloader] DB Migration Failure!'; exit 1 );

>&2 echo 'Web Services is now ready to start'

exec python3 manage.py runserver 0.0.0.0:8000 ;