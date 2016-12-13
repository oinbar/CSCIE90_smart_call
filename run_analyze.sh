#!/bin/bash



if [ ! -z $1 ]
then
    PROJECT_HOME=$1
else
    PROJECT_HOME=$(pwd)
fi



# create log files
TIMESTAMP=$(date +"%Y%m%d")
mkdir -p $PROJECT_HOME/log/$TIMESTAMP/
touch $PROJECT_HOME/log/$TIMESTAMP/analyzer.log
sudo chmod 777 -R $PROJECT_HOME/log

# create pid file
mkdir -p "$HOME/tmp"
PIDFILE="$HOME/tmp/analyzer.pid"
export PYTHONPATH=$PROJECT_HOME/:$PROJECT_HOME/src

if [ -e "${PIDFILE}" ] && (ps -p $(cat ${PIDFILE}) > /dev/null); then
  echo "application already running" >> $PROJECT_HOME/log/$TIMESTAMP/analyzer.log 2>&1 & 2>&1 &
  exit 99
fi

python $PROJECT_HOME/src/analyze.py >> $PROJECT_HOME/log/$TIMESTAMP/analyzer.log 2>&1 & 2>&1 &

echo $! > "${PIDFILE}"
chmod 644 "${PIDFILE}"