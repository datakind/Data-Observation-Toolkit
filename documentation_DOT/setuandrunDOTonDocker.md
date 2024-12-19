# Setting Up the Docker Environment and Running DOT
To build DOT from source, please follow the steps below:
1. **Set up your Python environment.**
2. **After cloning the repository, navigate to the repository's path:**
     - **For Windows:** 
       ```bash
       cd C:<PATH_TO_DOT>\Data-Observation-Toolkit\docker
       ```
     - **For Mac/Linux:**
       ```bash
       cd <PATH_TO_DOT>/Data-Observation-Toolkit/docker/
       ```
   - Alternatively, you can open a terminal and change the directory into the `docker` sub-directory of DOT:
        ```bash
         cd ./docker
        ```
3. **To save a PostgreSQL password to your local environment, use the following command in your terminal:**
 
     ```bash
      export POSTGRES_PASSWORD=<your_password_here>
     ```

4. This environment variable will be read and assigned with the value you provide at the time of setting up dot_db in the Docker Compose file.
    To build the Docker containers, run:

    ```bash
     docker compose build
     ```
**Note** in case you get an error related to ssh-agent, be sure to use the following:

  ```bash
   eval $(ssh-agent)      ==> for windows users 
   Or 
   eval ssh-agent       ==> for Mac/Linux users 
  ```

5. To start the containers, run:
   ```bash
     docker compose up -d
     ```
✅ Your containers should be running now!


### Running DOT
Once your docker containers are running you can use the following steps to run DOT via CLI.
1. ```bash
     docker exec -it dot /bin/bash
     ```
2.  ```bash
     cd dot
     ```
3.	 ```bash
     python3 ./run_everything.py --project_id 'ScanProject1'
     ```
These steps will execute the sample tests on the demo data and save the results to the DOT database.


### Setting up the DOT User Interface
To start the DOT user interface and manage the system, follow these steps. You will need to complete the initial setup the first time you use it:
1.	Navigate to [http://localhost:82/](http://localhost:82)
2.	Click the **Register** button to create a login (make sure to note the password, as it is specifically for the web application).
3.	After registration, click **'Build my own'** on the subsequent popup.
4.	Click the **Appsmith** icon in the top-left corner to return to the homepage.
5.	In the top-right corner, next to the **New** button, click on the ellipsis ('...') and select **Import**.
6.	Select **Import from file**, then navigate to the file ./docker/appsmith/DOT App V2.json.
7.	You will be prompted to enter details for the database connection. Set these parameters as needed, but if using the DOT Dockerized PostgreSQL database, use the following:
   
     - **Host address:** dot-db
     - **Port:** 5432
     - **Database name** dot_db
     - **Authentication > User name:** postgres
     - **Authentication > Password:** [THE PASSWORD YOU USED WHEN BUILDING DOT]
     
**You should now see the DOT user interface in developer mode, where you can edit it.**
To switch to end-user mode:

  1.	Click the button in the top-right corner and select **'Deploy'**. This will open a new tab displaying the user interface as it will appear to end users.
      
**Note:** If you wish to remove the Appsmith branding on the deployed app, append ?embed=True to the end of the deployed app URL.