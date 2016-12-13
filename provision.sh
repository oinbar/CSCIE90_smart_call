#!/bin/bash

# THIS ALL ASSUMES PYTHON 2.7.6
# IF UBUNTU 14.04 decides to ship a different python might need to work around that.


if [ ! -z $1 ]
then
    PROJECT_HOME=$1
else
    PROJECT_HOME=$(pwd)
fi




cd $PROJECT_HOME

apt-get update
apt-get -y install git
apt-get -y install unzip
apt-get -y install python-dev
apt-get -y install ipython-notebook
apt-get -y install python-numpy python-scipy python-pandas

# install setuptools and pip - this should work with a easy_install pip, but need to test...
wget https://pypi.python.org/packages/source/s/setuptools/setuptools-1.4.2.tar.gz
tar -xvf setuptools-1.4.2.tar.gz
cd setuptools-1.4.2
python setup.py install
cd ..
wget https://pypi.python.org/packages/source/p/pip/pip-7.1.2.tar.gz
tar -xvf pip-7.1.2.tar.gz
cd pip-7.1.2
python setup.py install
cd ..
rm -r pip-7.1.2
rm -r pip-7.1.2.tar.gz
rm -r setuptools-1.4.2
rm -r setuptools-1.4.2.tar.gz


# install python packages
pip install jupyter
pip install wget
sudo pip install pandas -U
sudo pip install boto
sudo pip install flask
sudo pip install twilio
sudo pip install gcloud
sudo pip install requests
sudo pip install oauth2client
sudo pip install google-api-python-client
sudo pip install gcs-oauth2-boto-plugin
#sudo pip install requirements.txt

# make data dir
mkdir data
mkdir data/raw
mkdir data/transcribed
mkdir data/tmp
sudo chmod -R 775 data

# set timezone
# sudo timedatectl set-timezone America/New_York

# INSTALL GCLOUD - THIS IS INTERACTIVE !!!!!!!
# Create an environment variable for the correct distribution
export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)"
# Add the Cloud SDK distribution URI as a package source
echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list
# Import the Google Cloud public key
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
# Update and installœ the Cloud SDK
sudo apt-get update && sudo apt-get install google-cloud-sdk
# Run gcloud init to get started - dont worry about this for now
# sudo gcloud init ### do this in startup phase, interactively?

echo PYTHONPATH='$PYTHONPATH':$PROJECT_HOME >> /etc/profile
echo PYTHONPATH='$PYTHONPATH':$PROJECT_HOME/src >> /etc/profile
echo export PYTHONPATH >> /etc/profile
source /etc/profile