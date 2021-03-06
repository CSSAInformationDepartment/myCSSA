#!/bin/bash

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
>&2 echo '#                             Version: 2.1b(C)                                #'
>&2 echo '#                                                                             #'
>&2 echo '###############################################################################'

yes | python3 manage.py makemigrations || { echo '[Bootloader] Migr2ation Check Failure!';  exit 1;}

python3 manage.py migrate --no-input || { echo '[Bootloader] DB Migration Failure!'; exit 1;}


if [ $DJANGO_SETTINGS_MODULE == 'CSSANet.settings.prod' ]; then
>&2 echo '[Bootloader] Web Services is booting up now in Production Settings'
exec gunicorn CSSANet.wsgi --workers=5 -b 0.0.0.0:8000 ;
# exec python3 manage.py celery worker --loglevel=info
else
python3 manage.py collectstatic --no-input || { echo '[Bootloader] Static Files Failure!';  exit 1; }
python3 manage.py loaddata createsuper.json || { echo '[Bootloader] Fixture Loading Failure!'; exit 1; }
>&2 echo '[Bootloader] Web Services is booting up now in Development Settings'
exec python3 manage.py runserver 0.0.0.0:8000 
fi