# This scripts sets up the ssh tunnel for accessing the Muso DB
#
# For more information please see this document:
#
# https://docs.google.com/document/d/1cx-4Ahz1-vEtuk9tw5K1o7ktRJP_CMPU5GvvAqaF83I/edit#
#

SSH_KEY_TO_MUSO="/home/ubuntu/.ssh/id_matt_github"

eval $(ssh-agent -s)
ssh-add $SSH_KEY_TO_MUSO

# Edit this line and change the login as needed
ssh -p 33696 datakindawsmatt@rdbms.dev.medicmobile.org -L 172.17.0.1:8110:localhost:5432 


