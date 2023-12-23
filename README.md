<p align="center">
<img src="./mascot.png" width="400" height="400">
</p>

# Find-a-Bug API

This repository defines a Python API for interacting with the [Find-A-Bug database](https://github.com/pipparichter/find-a-bug). It handles generation of URLs, submission of API requests to the web server, and parsing of plain-text responses from the server to `pandas` `DataFrames`.

## Installation

To install the API, first clone the repository using the following command. 

`git clone https://github.com/pipparichter/find-a-bug-api.git`

It's best practice to work within a `conda` (or equivalent) Python environment; `conda` can be installed [here](https://conda.io/projects/conda/en/latest/user-guide/install/index.html). To create a `conda` environment, run `conda create --name PROJECT_NAME`. Then, activate the environment with `conda activate PROJECT_NAME`. To install the Find-A-Bug API into this environment, simply navigate to the `find-a-bug-api` root directory and run `pip install -e` (or `pip install -e PATH_TO_DIRECTORY`). 

## Usage

Before accessing the Find-A-Bug database, you **must be connected to Caltech wifi** (or using the VPN). Instructions for connecting to the VPN can be found on the Caltech [website](https://www.imss.caltech.edu/services/wired-wireless-remote-access/Virtual-Private-Network-VPN). For more a more detailed usage guide, see the `demo.ipynb` notebook in the `notebooks` directory.