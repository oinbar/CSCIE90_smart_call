#!/usr/bin/env bash


if [ ! -z $1 ]
then
    PROJECT_HOME=$1
else
    PROJECT_HOME=$(pwd)
fi


cd $PROJECT_HOME
echo $PROJECT_HOME
export PYTHONPATH=$PROJECT_HOME/:$PROJECT_HOME/src


# create log files
TIMESTAMP=$(date +"%Y%m%d")
mkdir -p $PROJECT_HOME/log/$TIMESTAMP/
touch $PROJECT_HOME/log/$TIMESTAMP/apache.log
touch $PROJECT_HOME/log/$TIMESTAMP/mysql_init.log
sudo chmod 777 -R $PROJECT_HOME/log

# setup crontab
touch $PROJECT_HOME/cronfile

#### CRON FILE BELOW ############# - keep the spacing
cat <<EOF > $PROJECT_HOME/cronfile

PYTHONPATH=$PROJECT_HOME/:$PROJECT_HOME/src/

*/1 * * * * sh $PROJECT_HOME/run_application.sh $PROJECT_HOME

*/1 * * * * sh $PROJECT_HOME/run_analyze.sh $PROJECT_HOME

EOF


crontab cronfile $PROJECT_HOME/cronfile
rm $PROJECT_HOME/cronfile

# start services
# ipython notebook
ipython notebook --ip=0.0.0.0 &
# apache/phpmyadmin
#service apache2 restart >> $PROJECT_HOME/log/$TIMESTAMP/apache.log 2>&1 &

# run tests
nosetests -v