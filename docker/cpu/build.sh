#!/bin/sh
# Build the lightweight CPU-only DeOldify image
set -e

docker build -t deoldify-cpu -f ./Dockerfile ..
