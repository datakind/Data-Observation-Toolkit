"""This script will run the demo regardless of the users OS.Therefore,only this one file has to be maintained

Steps the script will have to do:
1)Download zipped tarfile from Google Drive (Hint:this should be done directly through python)
2)Unzip and untar it
3)Compose and run docker Containers
4)Access DOT-demo under http://localhost:82/app/data-observation-toolkit/run-log-634491ea0da61b0e9f38760d?embed=True
"""

import os
import shutil
import gdown
import tarfile
from python_on_whales import DockerClient  # had to be pip installed

# Check if db, appsmith and tar file are there and if so, delete them.
os.chdir("demo/")
if os.path.exists("db"):
    shutil.rmtree("db")
if os.path.exists("appsmith"):
    shutil.rmtree("appsmith")
if os.path.exists("dot_demo_data.tar"):
    os.remove("dot_demo_data.tar")

# Download Demo Data from Google Drive
print("Downloading demo data file ...")
url = "https://drive.google.com/uc?id=157Iad8mHnwbZ_dAeLQy5XfLihhcpD6yc"
output = "dot_demo_data.tar.gz"
gdown.download(url, output, quiet=False)
print("Download successful")

# Open/Extract tarfile
my_tar = tarfile.open('dot_demo_data.tar.gz')
my_tar.extractall('')  # specify which folder to extract to
my_tar.close()

# Composing and running container(s)
print("Starting DOT...")
os.chdir("../")
docker = DockerClient(compose_files=[os.getcwd() + os.sep + "docker-compose-demo.yml"])
docker.compose.down()
docker.compose.build(quiet=True)
docker.compose.up(quiet=False, )
