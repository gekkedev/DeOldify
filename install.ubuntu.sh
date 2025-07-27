#!/usr/bin/env bash
set -e

# Install dependencies for DeOldify on Ubuntu
sudo apt update
sudo apt install -y ffmpeg curl git jupyter-core

# Install Miniconda
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-py310_25.5.1-1-Linux-x86_64.sh -O ~/miniconda3/installer.sh
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
