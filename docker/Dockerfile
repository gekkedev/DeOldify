# Stage 1: image with full-featured ffmpeg for multistage processing
FROM jrottenberg/ffmpeg:4.4-ubuntu AS ffmpeg_stage

# Stage2: Use an official PyTorch runtime as a parent image
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

# Set the working directory in the container
WORKDIR /app

# to avoid prompts during APT package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies and clean up
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       wget \
       libgl1 libglib2.0-0 libgomp1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# uninstall the (too) thin ffmpeg that was preinstalled via Conda
RUN conda remove -y ffmpeg

# manually copy over the ffmpeg binary (it has the required --enable-libx264 flag)
COPY --from=ffmpeg_stage /usr/local/bin/ffmpeg /usr/local/bin/ffmpeg
COPY --from=ffmpeg_stage /usr/local/bin/ffprobe /usr/local/bin/ffprobe
# lots of .so files because of this ffmpeg build being dynamically linked:
COPY --from=ffmpeg_stage /usr/local/lib /usr/local/lib
#prepend the library path to include the copied ffmpeg libraries
ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

# Copy the project into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-common.txt

# Download the pre-trained models for image and video colorization
# These are large files, so it may take some time to download
RUN wget https://data.deepai.org/deoldify/ColorizeArtistic_gen.pth -O ./models/ColorizeArtistic_gen.pth && \
    wget https://www.dropbox.com/s/axsd2g85uyixaho/ColorizeStable_gen.pth?dl=0 -O ./models/ColorizeStable_gen.pth && \
    wget https://data.deepai.org/deoldify/ColorizeVideo_gen.pth -O ./models/ColorizeVideo_gen.pth

# Trigger the ResNet checkpoint (model weights) download by loading the models once which results in the checkpoint being downloaded
RUN python -c "from deoldify.visualize import *; get_video_colorizer(); get_image_colorizer(); get_image_colorizer(artistic=False)"

# Default command runs an interactive Python session
CMD ["python"]