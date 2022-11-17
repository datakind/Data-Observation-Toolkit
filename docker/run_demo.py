"""This script will run the DOT demo"""

import os
import shutil
import time
import tarfile
import webbrowser
import gdown
from python_on_whales import DockerClient

url_demo_data = "https://drive.google.com/uc?id=157Iad8mHnwbZ_dAeLQy5XfLihhcpD6yc"
filename_demo_data = "dot_demo_data.tar.gz"
url_dot_ui = "http://localhost:82/app/data-observation-toolkit/run-log-634491ea0da61b0e9f38760d?embed=True"

# Check if db, appsmith and tar file are there and if so, delete them.
os.chdir("demo/")
if os.path.exists("db"):
    shutil.rmtree("db")
if os.path.exists("appsmith"):
    shutil.rmtree("appsmith")
if os.path.exists("dot_demo_data.tar"):
    os.remove("dot_demo_data.tar")

print("\nDownloading demo data file....\n")

# Download Demo Data from Google Drive
gdown.download(url_demo_data, filename_demo_data, quiet=False)

print("Demo data has been downloaded\n")

# Open/Extract tarfile
with tarfile.open(filename_demo_data) as my_tar:
    my_tar.extractall('')
    my_tar.close()

with open("./db/.env") as f:
    demo_pwd=f.read().split("=")[1]
    os.environ['POSTGRES_PASSWORD'] = demo_pwd

# Composing and running container(s)
print("Starting DOT...\n")
os.chdir("../")
docker = DockerClient(compose_files=[os.getcwd() + os.sep + "docker-compose-demo.yml"])
docker.compose.down(quiet=True)
docker.compose.up(quiet=True, build=True, detach=True)

print("Waiting for DOT to start, time to make a nice cup of tea! ☕ ...\n")
time.sleep(20)

webbrowser.open(url_dot_ui)

print("In case DOT was not opened in your browser, please go to this URL: "
      "http://localhost:82/app/data-observation-toolkit/run-log-634491ea0da61b0e9f38760d?embed=True\n")
input("Press return to stop DOT container\n")
print("Container is being stopped - we hope you enjoyed this demo :)")
docker.compose.stop()
