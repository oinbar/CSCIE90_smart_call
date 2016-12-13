To run local vagrant environment:
    1. install vagrant
    2. clone this repo
    3. cd into lamp-backend-pipeline and run $ vagrant up (this will also trigger provision_ubuntu.sh 
       and startup_ubuntu.sh)
    4. ssh in with $ vagrant ssh or access notebooks on HOST at localhost:8889, and ui at localhost:8001    

To run the server:
    1. ssh into server:
        $ ssh -i ~/Dropbox/School/cloud_iot/e90-key2.pem ubuntu@50.16.213.90
    2. Provision/startup the server: 
        $ sudo apt-get update
        $ sudo apt-get install git 
        $ git clone https://github.com/oinbar/smart_call.git
        $ cd smart_call
        $ sudo sh provision.sh
        $ sh startup.sh
    3.  go throug the google cloud initialization process.. eventually this should be automated...
        $ sudo gcloud init
            proj id: smartcaller-145902
        $ sudo gcloud auth login
            application should now have implicit access to bucket


    TODO code:
    - dont use cron job to analyze recordings, should be kicked off asynchronously. recording url should be
      put in a queue

    dont re-auth app everytime. reuse access key.
    use python api, not bash commands where possible.
    do better job of launching async calls of scripts. cron is ok, but not optimal.
    improve logging, need a real logger
    add language in json

    TODO features:
    add dual channel support from twilio. this will be huge, for conversations.
