# Simple install script to install Python dependencies, dbt and ge

# Python packages
pip install --upgrade pip
# Based on this https://stackoverflow.com/questions/69287269/installing-ruamel-yaml-clib-with-docker.
pip install -U pip setuptools wheel ruamel.yaml ruamel.yaml.clib==0.2.6
pip install -r requirements_dot.txt
