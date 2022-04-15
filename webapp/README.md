# DOT Simple Web app

POC Web app for setting configured tests, modifications of these repos:

[https://github.com/olinations/crud-starter-api](https://github.com/olinations/crud-starter-api)
[https://github.com/olinations/crud-starter-frontend-hooks](https://github.com/olinations/crud-starter-frontend-hooks)

Just exploration at this point. 

# To setup

## Generating DOT results 

First, you will need to follow the instructions to set up the main DOT. Follow [these steps](https://github.com/datakind/medic_data_integrity/blob/main/README.md#super-duper-quick-start-for-alpha-release-january-2022).

This will give you a DB with data, running in Docker. 

## Building the web app

1. cd `docker`
2. Uncomment the sections in docker-compose.yml related to the web app
3. `docker compose build`
4. `docker compose up -d`

## Manually running the web app outside of Docker

If you prefer to not use Docker, you can run the web app as follows ...

1. `cd server`
2. `npm install`
3. Create a file called `.env` in `./server` which looks like this (but with your database crednetials)...

```
DB_HOST=localhost
DB_PORT=5433
DB_USER=postgres
DB_PASSWORD=password124
DB_DATABASE=dot_db
DB_SCHEMA=dot
DB_DEBUG=true
PORT=3002
WHITELIST=http://localhost:3000
```
4. `cd ../frontend`
5. `npm install`
6. Create a file called `.env` which has contents like this ...

```
API_SERVER=http://localhost:3002/crud
```

Make sure your API_SERVER is set to the right host and port as defined in step 3.

# To start web app

1. Start the back end API server: 
   - `cd server`
   - `npm start`
2. Start the
   - `cd frontend`
   - `npm start`
   - When prompted, accept the run on another port
   
# To use the web app

Go to `http://localhost:3000/crud`

You can also check the API is working by going to this in your browser:

`http://localhost:3002/crud`
