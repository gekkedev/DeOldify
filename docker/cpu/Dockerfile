# Lightweight CPU-only image for DeOldify video colorization
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Avoid interactive prompts during package installs
ENV DEBIAN_FRONTEND=noninteractive

# Install minimal system dependencies and ffmpeg
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg libgl1 libglib2.0-0 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy project files into the container
COPY . .

# Install only the Python packages needed for CPU inference
RUN pip install --no-cache-dir -r requirements-cpu.txt

# Fetch the video model weights; this avoids download at runtime
RUN wget https://data.deepai.org/deoldify/ColorizeVideo_gen.pth -O ./models/ColorizeVideo_gen.pth

# Warm up the model once so that supporting weights are cached
RUN python - <<'PY'
from deoldify.visualize import get_video_colorizer
get_video_colorizer()
PY

# Process all videos found in /app/video/source when the container runs
CMD ["python", "VideoColorizer.py"]
