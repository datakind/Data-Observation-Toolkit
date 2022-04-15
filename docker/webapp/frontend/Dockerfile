FROM node:13

# Create app directory
WORKDIR /usr/src/app

COPY ./webapp/server/package.json ./

RUN npm install

CMD [ "npm", "start" ]
#CMD tail -f /dev/null
