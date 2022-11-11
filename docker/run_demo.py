'''This script will run the demo regardless of the users OS.Therefore,only this one file has to be maintained
instead of one ps1 for windows and one sh for linux
Steps the script will have to do:
1)Download zipped tarfile from google drive (Hint:this should be done directly through python)
2)Unzip and untar it(HINT:Should also be possible through python-if not,import)
3)Composedocker Containers
4)Access DOT-demo under http://localhost:82/app/data-observation-toolkit/run-log-634491ea0da61b0e9f38760d?embed=True
TIPP:Avoid system commands in python code but use libraries etc.!
'''

import os
import shutil
import gdown
import tarfile
import docker

#Had to be pip installed
#Check if db, appsmith and tar file are there and if so, delete them.
#Idea: Use path relative to this file - has to be changed if the file is moved

os.chdir("demo/")
if os.path.exists("db"):
    shutil.rmtree("db")
if os.path.exists("appsmith"):
    shutil.rmtree("appsmith")
if os.path.exists("dot_demo_data.tar"):
    os.remove("dot_demo_data.tar")

#Download Demo Data from Google Drive
#QUESTION: Can import gdown library alternatively - any pros or cons?
print("Downloading demo data file ...")
url = "https://drive.google.com/uc?id=157Iad8mHnwbZ_dAeLQy5XfLihhcpD6yc"
output = "dot_demo_data.tar.gz"
gdown.download(url, output, quiet=False)
print("download successful")

#Open/Extract tarfile
my_tar = tarfile.open('dot_demo_data.tar.gz')
my_tar.extractall('') # specify which folder to extract to
my_tar.close()

#Starting DOT (composing Container)
#os.system("cd.. && docker compose -f docker-compose-demo.yml build && docker compose -f docker-compose-demo.yml up -d")

print(os.curdir)
client = docker.from_env()
client.containers.create(image='alpine')

print("Starting DOT ...")
print("Waiting for DOT to start, time to make a nice cup of tea! ☕ 😃 ...")
print("Open a browser and go to this URL: \n http://localhost:82/app/data-observation-toolkit/run-log-634491ea0da61b0e9f38760d?embed=True")
print("To STOP DOT run this command: docker compose -f docker-compose-demo.yml stop")
