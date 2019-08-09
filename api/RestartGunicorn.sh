#!/bin/bash

echo "===> activating the virtual env"
source "./venv/bin/activate"
sleep 1

echo
echo "===> killing currently running workers of gunicorn"
pkill gunicorn
sleep 1

echo
echo "===> restarting gunicorn with 3 workers on Port 8080"
nohup gunicorn --workers 3 --bind :8080 -m 007 application:app > gunicorn.log 2>&1 &

echo
echo "===> to see log: tail -f gunicorn.log"

exit
