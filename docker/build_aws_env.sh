# This script runs all the commands to deploy an airflow environment to an AWS server.#
#
# For more details, please refer to this DataKind google document:
#
# https://docs.google.com/document/d/1cx-4Ahz1-vEtuk9tw5K1o7ktRJP_CMPU5GvvAqaF83I/edit#
#
#

SSH_KEY_TO_MUSO="/home/ubuntu/.ssh/id_matt_github"

eval $(ssh-agent -s)
ssh-add $SSH_KEY_TO_MUSO

docker-compose -f docker-compose-with-airflow.yml stop
docker-compose -f docker-compose-with-airflow.yml build
docker-compose -f docker-compose-with-airflow.yml up airflow-init
docker-compose -f docker-compose-with-airflow.yml up -d
docker exec -ti docker_airflow-worker_1 sh -c "cd /app/dot && ./install_dot.sh"

