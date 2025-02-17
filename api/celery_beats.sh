#! /bin/sh
echo "celery beats"
if [ -d ".env" ];
then
    echo ".env folder exists. Runningcelery beats"
else
    echo "creating .env and install using pip"
    virtualenv .env
fi

# Activate virtual env
. .env/bin/activate


celery -A imports.celery beat --loglevel=info
