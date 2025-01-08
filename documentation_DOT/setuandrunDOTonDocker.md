# Setting Up the Docker Environment and Running DOT
### To build DOT from source, please follow the steps below:
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
   eval $(ssh-agent)    ==> for windows users
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

     <figure style="text-align:center;">
      <figcaption></figcaption>
      <img src="https://github.com/wvelebanks/Data-Observation-Toolkit/blob/f5a7a35828a871e5f7b9f6c9d03aee8f6f762d89/images/appsmith_signup.png" alt="dot_appsmith1" />
    </figure>

3.	After registration, click **'Create Now'**  button  at the top right corner

      <figure style="text-align:center;">
       <figcaption></figcaption>
       <img src="https://github.com/wvelebanks/Data-Observation-Toolkit/blob/f5a7a35828a871e5f7b9f6c9d03aee8f6f762d89/images/importDOTonAppsmith.png" alt="dot_appsmith2" />
     </figure>

     and the click on **'import file'** a popup window will request you to upload the file or application:

      <figure style="text-align:center;">
       <figcaption></figcaption>
       <img src="https://github.com/wvelebanks/Data-Observation-Toolkit/blob/f5a7a35828a871e5f7b9f6c9d03aee8f6f762d89/images/importappsmithapp.png" alt="dot_appsmith3" />
     </figure>

4.	Click the **Appsmith** icon in the top-left corner to return to the homepage.
5.	In the top-right corner, next to the **New** button, click on the ellipsis ('...') and select **Import**.
6.	Select **Import from file**, then navigate to the file ```./docker/appsmith/DOT``` App V2.json.

     <figure style="text-align:center;">
       <figcaption></figcaption>
       <img src="https://github.com/wvelebanks/Data-Observation-Toolkit/blob/29960ed70da625ae75a1272286720c77df5171c0/images/importingDOTapptoAppsmith.png" alt="dot_appsmith4" />
     </figure>

7.	You will be prompted to enter details for the database connection. Set these parameters as needed, but if using the DOT Dockerized PostgreSQL database, use the following:

     - **Host address:** dot-db
     - **Port:** 5432
     - **Database name** dot_db
     - **Authentication > User name:** postgres
     - **Authentication > Password:** [THE PASSWORD YOU USED WHEN BUILDING DOT]


     <figure style="text-align:center;">
       <figcaption></figcaption>
       <img src="https://github.com/wvelebanks/Data-Observation-Toolkit/blob/bd12481733f398e3dcf69c555631f9baf137aa0a/images/dbconnection_on_appsmisth.png" alt="dot_appsmith5" />
     </figure>

   once connected you should see te following information about the database:

      <figure style="text-align:center;">
       <figcaption></figcaption>
       <img src="https://github.com/wvelebanks/Data-Observation-Toolkit/blob/48cf09c1bb328baca5271a53db38e28679005e87/images/dbconnectedtoappsmith.png" alt="dot_appsmith7" />
     </figure>


**You should now see the DOT user interface in developer mode, where you can edit it.**
To switch to end-user mode:

  1.	Click the button in the top-right corner and select **'Deploy'**. This will open a new tab displaying the user interface as it will appear to end users.

**Note:** If you wish to remove the Appsmith branding on the deployed app, append ?embed=True to the end of the deployed app URL.


If you need to [set up the database for DOT](https://github.com/wvelebanks/Data-Observation-Toolkit/blob/b70d3e044858387443698354b0c4253a6b618b17/documentation_DOT/configuringDOTdb.md) or [configure Appsmith](https://github.com/wvelebanks/Data-Observation-Toolkit/blob/d9845f8228bb147af7f28f7a300a68012e9b51ed/documentation_DOT/developingappsmith.md), check out the guide for setting up the DOT Database and the guide for configuring Appsmith. These resources will provide step-by-step instructions for both tasks.