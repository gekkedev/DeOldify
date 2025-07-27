# loosely copied from https://github.com/daddyparodz/AutoDeOldifyLocal
# needs adaptions to be working on Linux without the user being a pytorch veteran
# tested in a Ubuntu 23.04 context w/ Codex

sudo apt update # so that ffmpeg can even be found
# && sudo apt upgrade -y # left out for now as we rather have an outdated, but stable machine
sudo apt install -y ffmpeg curl git jupyter-core

# install miniconda
mkdir -p ~/miniconda3
#wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/installer.sh # latest installer
wget https://repo.anaconda.com/miniconda/Miniconda3-py310_25.5.1-1-Linux-x86_64.sh -O ~/miniconda3/installer.sh
# version frozen intentionally for compat; occasionally check for minor/patch updates here: https://repo.anaconda.com/miniconda/
bash ~/miniconda3/installer.sh -b -u -p ~/miniconda3
rm ~/miniconda3/installer.sh

# to circumvent Conda SSL issues
~/miniconda3/bin/conda config --set ssl_verify "${CODEX_PROXY_CERT}"
# Optional: explicitly set proxy in Conda (not usually needed)
# conda config --set proxy_servers.http "$http_proxy"
# conda config --set proxy_servers.https "$https_proxy"

#not doing anything here?
#~/miniconda3/bin/conda init
#source ~/.bashrc

# Create the conda environment
~/miniconda3/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
~/miniconda3/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
#~/miniconda3/bin/conda env create python=3.10 -f environment.yml -y
~/miniconda3/bin/conda env create -f environment.yml -y

# Download the model file
#MODEL_PATH="models/ColorizeArtistic_gen.pth"
#if [ ! -f "$MODEL_PATH" ]; then
#    echo "Downloading model file..."
#    curl -L https://huggingface.co/spaces/aryadytm/photo-colorization/resolve/main/models/ColorizeArtistic_gen.pth?download=true -o $MODEL_PATH
#else
#    echo "Model file already exists."
#fi

~/miniconda3/bin/conda init
source ~/.bashrc

~/miniconda3/bin/conda activate deoldify
jupyter server --generate-config