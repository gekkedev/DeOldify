# Use an official PyTorch runtime as a parent image
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

# Set the working directory in the container
WORKDIR /app

# Install system dependencies and clean up
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ffmpeg git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirement files to install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project into the container
COPY . .

# Default command runs an interactive Python session
CMD ["python"]
