#!/bin/bash

set -e

# Exit early if the desired version is already the default.
if python3 --version 2>/dev/null | grep -q '^Python 3\.10'; then
    echo "Python 3.10 already installed. Skipping installation."
    exit 0
fi

# Script to install Python 3.10 on Ubuntu systems

echo "Updating system and installing prerequisites..."
sudo apt update
sudo apt install -y software-properties-common

echo "Adding deadsnakes PPA (if not already added)..."
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

echo "Installing Python 3.10 and related packages..."
sudo apt install -y python3.10 python3.10-venv python3.10-distutils

echo "Setting Python 3.10 as the default python3 interpreter..."
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

echo "You can now choose your default python3 version manually if needed:"
sudo update-alternatives --set python3 /usr/bin/python3.10

echo "Checking Python version..."
python3 --version

