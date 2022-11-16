"""This script will run the demo regardless of the users OS.Therefore,only this one file has to be maintained
Steps the script will have to do:
1)Download zipped tarfile from Google Drive (Hint:this should be done directly through python)
2)Unzip and untar it
3)Compose and run docker Containers
4)Access DOT-demo under http://localhost:82/app/data-observation-toolkit/run-log-634491ea0da61b0e9f38760d?embed=True
"""

import os
import shutil
import time
import tarfile
import webbrowser
import base64
import gdown
from python_on_whales import DockerClient

url_demo_data = "https://drive.google.com/uc?id=157Iad8mHnwbZ_dAeLQy5XfLihhcpD6yc"
filename_demo_data = "dot_demo_data.tar.gz"
password = str(base64.b64decode(b'cGFzc3dvcmQxMjU='), "UTF-8")
url_dot_ui = "http://localhost:82/app/data-observation-toolkit/run-log-634491ea0da61b0e9f38760d?embed=True"

# Set environment variable for later use
os.environ['POSTGRES_PASSWORD'] = password

# Check if db, appsmith and tar file are there and if so, delete them.
os.chdir("demo/")
if os.path.exists("db"):
    shutil.rmtree("db")
if os.path.exists("appsmith"):
    shutil.rmtree("appsmith")
if os.path.exists("dot_demo_data.tar"):
    os.remove("dot_demo_data.tar")

# Download Demo Data from Google Drive
gdown.download(url_demo_data, filename_demo_data, quiet=False)

# Open/Extract tarfile
my_tar = tarfile.open(filename_demo_data)
my_tar.extractall('')
my_tar.close()

# Composing and running container(s)
print("Starting DOT...")
os.chdir("../")
docker = DockerClient(compose_files=[os.getcwd() + os.sep + "docker-compose-demo.yml"])
docker.compose.down(quiet=True)
docker.compose.up(quiet=True, build=True, detach=True)

time.sleep(45)

webbrowser.open(url_dot_ui)

input("Press any key to stop DOT container")
docker.compose.stop()
