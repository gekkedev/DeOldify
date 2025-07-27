#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(dirname "$0")"

# Ensure the desired Python version is installed
"${SCRIPT_DIR}/install-python3.10.sh"

# loosely copied from https://github.com/daddyparodz/AutoDeOldifyLocal
# needs adaptions to be working on Linux without the user being a pytorch veteran
# tested in a Ubuntu 23.04 context w/ Codex

# Install dependencies for DeOldify on Ubuntu
sudo apt update # so that ffmpeg can even be found
# && sudo apt upgrade -y # left out for now as we rather have an outdated, but stable machine
sudo apt install -y ffmpeg curl git jupyter-core


# Install Miniconda
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-py310_25.5.1-1-Linux-x86_64.sh -O ~/miniconda3/installer.sh
#wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/installer.sh # latest installer
# version frozen intentionally for compat; occasionally check for minor/patch updates here: https://repo.anaconda.com/miniconda/
bash ~/miniconda3/installer.sh -b -u -p ~/miniconda3
rm ~/miniconda3/installer.sh

# Create the conda environment
~/miniconda3/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
~/miniconda3/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
~/miniconda3/bin/conda env create -f environment.yml -y

# Initialize conda and activate the environment
~/miniconda3/bin/conda init
source ~/.bashrc
~/miniconda3/bin/conda activate deoldify

# Generate a Jupyter configuration
jupyter server --generate-config
