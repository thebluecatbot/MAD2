#! /bin/sh

if [ -d ".env" ];
then
    echo ".env folder exists. Installing using pip"
else
    echo "creating .env and install using pip"
    virtualenv .env
fi

# Activate virtual env
. .env/bin/activate

# Make sure redis server is running
service redis-server restart

# Upgrade the PIP
pip install --upgrade pip
pip install -r requirements.txt

# Now activate the venv and run main.py
