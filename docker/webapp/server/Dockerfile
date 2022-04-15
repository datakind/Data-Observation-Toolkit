FROM node:13

# Create app directory
WORKDIR /usr/src/app

COPY ./webapp/server/package.json ./

RUN npm install

# Install psql, useful
RUN apt-get -y update
RUN apt-get -y install postgresql-client

CMD [ "npm", "start" ]
#CMD tail -f /dev/null
