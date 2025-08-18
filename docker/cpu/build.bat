@echo off
REM Build the lightweight CPU-only DeOldify image
docker build -t deoldify-cpu -f ./Dockerfile ..
