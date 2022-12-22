# TDEI-Python-ms-core
## Core Package for microservices using Python
This will mimic the functionality available in https://github.com/TaskarCenterAtUW/TDEI-node-ms-core, but in Python.
Python version to use - 3.10.3 (with type hinting)

### Setting python environment
#### Using provided script
```
source setup_env.sh
```
does the checks to see if you have conda installed on the system, makes sure you dont already have a tdei env, and if these checks pass, installs the env, and the required packages

#### Manual creation
`conda` is useful to set up the environment with specific Python version
It is assumed the developer has `conda` installed on the dev machine
To create an environment called 'tdei' with the specific python version (3.10.3)
```
conda create -n tdei python==3.10.3
```
Activate the environment with:
```
conda activate tdei
```
To install the required packages needed to run the code:
```
pip install -r requirements.txt
```