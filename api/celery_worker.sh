#! /bin/sh

echo "celery worker"
if [ -d ".env" ];
then
    echo ".env folder exists. Running celery worker"
else
    echo "creating .env and install using pip"
    virtualenv .env
fi

# Activate virtual env
. .env/bin/activate


celery -A imports.celery worker --loglevel=info
