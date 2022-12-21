#!/bin/bash
env_name="tdei"
# check if conda exists in the system
conda_path=$(which conda)
echo $conda_path
echo "Checking if conda is installed on the system ..."
if ! hash which conda 2>/dev/null
then 
    echo " conda not found on the system"
    echo " !!! Please install conda on your system before proceeding ..."
    return 1
else
    echo " found conda at $conda_path"
fi

echo "Checking if the environment already exists ..."
if conda env list | grep "$env_name" >/dev/null 2>&1
then
    echo " !!! $env_name already in the system. Exiting..."
    return 1
fi 

echo "Creating $env_name env with conda ..."
y | conda create -n $env_name python==3.10.3 

echo "Activating $env_name ..."
source ~/anaconda3/etc/profile.d/conda.sh
conda activate $env_name

echo "Installing required packages using pip in $env_name ..."
pip install -r requirements.txt
echo " ***********************************************"
echo "   TDEI env set up and activation complete..."
echo " ***********************************************"