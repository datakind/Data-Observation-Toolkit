#!/usr/bin/env bash
# Simple install script to install Python dependencies, dbt and ge
set -euo pipefail

# Python packages
# pip install --upgrade pip
pip install "pip<22" \
            "setuptools>=59.1.1,<59.7.0" \
            "wheel<0.45" \
            "packaging<22"

# Based on this https://stackoverflow.com/questions/69287269/installing-ruamel-yaml-clib-with-docker.
# pip install -U pip setuptools wheel ruamel.yaml ruamel.yaml.clib==0.2.6
pip install "ruamel.yaml" "ruamel.yaml.clib==0.2.6"

pip install -r requirements_dot.txt

# sanity check
pip check