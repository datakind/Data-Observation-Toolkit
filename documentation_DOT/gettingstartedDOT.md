# Getting Started with DOT
### Video Demo of DOT 

[![Video Thumbnail](https://user-images.githubusercontent.com/8402586/195226567-fe035544-7075-4750-8bd8-ddfa7f57a811.jpg)](https://user-images.githubusercontent.com/8402586/195226567-fe035544-7075-4750-8bd8-ddfa7f57a811.mp4)

**Note:** Be sure to activate audio 
The quickest way to start using DOT is by utilizing the provided Docker environment and demo data. If you've already installed the required software (as per the general prerequisites), follow these steps:
1.	Download or clone the DOT repository to your computer.
2.	Start Docker.
3.	Open a terminal and navigate to the docker folder inside your DOT installation directory:

      - **For Windows:**
       ```bash
        cd C:<PATH_TO_DOT>\Data-Observation-Toolkit\docker
       ```
     - **For Mac/Linux:**
       ```bash
        cd <PATH_TO_DOT>/Data-Observation-Toolkit/docker/
       ```
4.	On Mac/Linux, run python3 ```run_demo.py```. On Windows, run python3 ```.\run_demo.py```.
5.	The script will launch DOT and open a browser window with the [DOT User Interface](http://localhost:82/app/data-observation-toolkit/run-log-634491ea0da61b0e9f38760d?embed=True). Refer to the demo video above for a step-by-step guide.
6.	When you're finished with the demo, press **Return** in the terminal to stop the Docker containers.


To explore DOT in more depth, refer to the guides on setting it up: for running DOT in a Docker environment, check out the [Docker Environment to Run DOT guide](https://github.com/wvelebanks/Data-Observation-Toolkit/blob/e95231bdaf4c8410633b298ac246173b061dbe52/documentation_DOT/setuandrunDOTonDocker.md), and for deploying DOT to Airflow, see the [Deploying DOT to Airflow guide](https://github.com/wvelebanks/Data-Observation-Toolkit/blob/72a3bb7a36fbfc69b621180fd52034dc99d1ee86/documentation_DOT/airflowdeployment.md). These resources provide step-by-step instructions for setting up and using DOT in different environments.