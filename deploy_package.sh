#!/bin/sh

# VARS
DT=$(date +%FT%T)
PROJ_NAME="python-ms-core"
BUILD_FOLDER="build"
BUILD_TARGET="$BUILD_FOLDER/$PROJ_NAME/python"

rm -rf $BUILD_TARGET

# Build requirements.txt
pipenv lock --requirements > requirements.txt

# Download/install requirements
pip install -r requirements.txt -t $BUILD_TARGET

# Install self
pip install . -t $BUILD_TARGET