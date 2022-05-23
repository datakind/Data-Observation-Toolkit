FROM python:3.8-slim-buster

WORKDIR app/

RUN apt-get update

RUN pip install --upgrade pip

# This uses the requirements as defined in the dot directory
COPY ./dot/requirements_data_confidence.txt requirements_data_confidence.txt
COPY ./dot/install_dot.sh install_dot.sh
RUN ./install_dot.sh

# In order to run tests from the docker instance
COPY ./dot/requirements_test.txt requirements_test.txt

# Install psql, useful
RUN apt-get -y install postgresql-client

#CMD [ "python3" ]
CMD tail -f /dev/null
