#
# Script to download data file and run DOT demo.
#
#!/bin/bash

# First clean up any previous demos
cd demo && rm -rf ./db && rm -rf ./appsmith && rm *.tar* && cd ..

echo "Downloading demo data file ..."
# See scrip upload_demo_to_dockerhub.sh to see how this URL file was created
# File is in this folder: https://drive.google.com/drive/folders/18p5Alxy7wR7cO6w4FD_o3zIsXHCe-RyR
# File link: https://drive.google.com/file/d/157Iad8mHnwbZ_dAeLQy5XfLihhcpD6yc/view?usp=sharing
fileid="157Iad8mHnwbZ_dAeLQy5XfLihhcpD6yc"
filename="./demo/dot_demo_data.tar.gz"
curl -c ./cookie -s -L "https://drive.google.com/uc?export=download&id=${fileid}" > /dev/null
curl -Lb ./cookie "https://drive.google.com/uc?export=download&confirm=`awk '/download/ {print $NF}' ./cookie`&id=${fileid}" -o ${filename}

echo "Unpacking demo data ..."
cd demo && gunzip dot_demo_data.tar.gz && tar -xvf dot_demo_data.tar && cd ..

echo "Starting DOT ..."
export POSTGRES_PASSWORD=password125   # This is only to demo fake data
docker compose -f docker-compose-demo.yml stop
docker compose -f docker-compose-demo.yml build
sleep 5
docker compose -f docker-compose-demo.yml up -d

echo "Waiting for DOT to start, time to make a nice cup of tea! ☕ 😃 ..."
sleep 30

# This is the APP shared with 'public' set to on, so use doesn't have to log in
echo "Open a browser and go to this URL: "
echo
echo "         http://localhost:82/app/data-observation-toolkit/run-log-634491ea0da61b0e9f38760d?embed=True"
echo
echo "To STOP DOT run this command: docker compose -f docker-compose-demo.yml stop"