# # First clean up any previous demos
cd demo
if (test-path './db') {
    remove-item './db' -Recurse
  }
if (test-path './appsmith') {
remove-item './appsmith' -Recurse
}
if (test-path '*.tar*') {
remove-item '*.tar*' 
}


# Download test data
wget "https://drive.google.com/uc?export=download&id=157Iad8mHnwbZ_dAeLQy5XfLihhcpD6yc" -O "dot_demo_data.tar.gz" 
bash gunzip dot_demo_data.tar.gz 
bash tar -xvf dot_demo_data.tar
cd ..

Write-Output "Starting DOT ..."

set POSTGRES_PASSWORD=password125
docker compose -f docker-compose-demo.yml down -v
docker compose -f docker-compose-demo.yml build
sleep 5
docker compose -f docker-compose-demo.yml up -d

Write-Output "Waiting for DOT to start, time to make a nice cup of tea! ☕ 😃 ..."


$Dotupcheck= $false
While ($Dotupcheck= $false){
$Dotdemostatus=docker ps --filter "ancestor=datakindorg/dot_appsmith"
if ($Dotdemostatus[1] -contains "healthy") { 
    $Dotupcheck= $true
  }
  else {
    sleep 5
  }
}
Write-Output "Open a browser and go to this URL: "
Write-Output "         http://localhost:82/app/data-observation-toolkit/run-log-634491ea0da61b0e9f38760d?embed=True"
Write-Output "To STOP DOT run this command: docker compose -f docker-compose-demo.yml stop"