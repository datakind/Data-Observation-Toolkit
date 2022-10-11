#
# A helper script to tag and upload build docker images to docker hub, so they can be used in demo
# docker compose.
#
# The process is:
#
# Generate demo data files by buiulding docker, setting up Appsmith and doing a few DOT runs ...
#
# 1. export POSTGRES_PASSWORD and then `docker compose build` and `docker compose up -d`
# 2. Go through the install instruction in the README. For appsmith, user should be dot@datakind.org and the password in README
#      - This login is only on the local Docker appsmith, with access to fake data
# 3. Import app JSON file from ./appsmith
# 4. Run DOT a few times to generate some data (see README)
# 5. cd ./demo && tar -cvf dot_demo_data.tar ./db ./appsmith && gzip dot_demo_data.tar
# 6. Upload the zipped tarfile here: https://drive.google.com/drive/folders/18p5Alxy7wR7cO6w4FD_o3zIsXHCe-RyR
#
# Then push the docker build to dockerhub ...
#
# 7. Log into docker hub via docker desktop, using datakind login
# 8. Then run this script to push images
#
#
# Once up on Docker hub, a user can run the demo by running script `run_dot_demo.sh`
#
docker commit dot datakind/dot_demo:latest
docker commit dot-db datakind/dot_db_demo:latest
docker commit appsmith datakind/dot_appsmith:latest
docker push datakind/dot_demo:latest
docker push datakind/dot_db_demo:latest
docker push datakind/dot_appsmith:latest