#NOTE:  This must be the first call in order to work properly!
import os  # Allow device selection via environment variable
from deoldify import device
from deoldify.device_id import DeviceId
# choices:  CPU, GPU0...GPU7
# Default to CPU so this script works in lightweight containers
_device_str = os.getenv("DEOLDIFY_DEVICE", "CPU").upper()
try:
    device.set(device=DeviceId[_device_str])
except KeyError:
    device.set(device=DeviceId.CPU)

import torch
print("CUDA available: " + str(torch.cuda.is_available()))

from deoldify.visualize import *
plt.style.use('dark_background')
import warnings
warnings.filterwarnings("ignore", category=UserWarning, message=".*?Your .*? set is empty.*?")

print("Loading video colorizer...")
colorizer = get_video_colorizer()
print("Video colorizer loaded.")

#NOTE:  Max is 44 with 11GB video cards.  21 is a good default
render_factor=21
#NOTE:  Make source_url None to just read from file at ./video/source/[file_name] directly without modification
source_url = None
#source_url='https://twitter.com/silentmoviegifs/status/1116751583386034176'

# read and process the entire video folder
import subprocess
folder_path = 'video/source'
result_path = None
for file_name in os.listdir(folder_path):
    file_path = os.path.join(folder_path, file_name)

    # Skip if it's not a file
    if not os.path.isfile(file_path):
        print(f"Skipping: {file_name} (not a file)")
        continue

    base, ext = os.path.splitext(file_name)

    # Convert non-mp4 files to mp4 using ffmpeg's stream copy for lossless re-containerization
    if ext.lower() != '.mp4':
        mp4_name = base + '.mp4'
        mp4_path = os.path.join(folder_path, mp4_name)

        if os.path.exists(mp4_path):
            # Reuse the existing MP4 to avoid unnecessary work
            print(
                f"Conversion skipped for {file_name}: {mp4_name} exists, assuming it was previously converted"
            )
        else:
            cmd = ['ffmpeg', '-y', '-i', file_path, '-c', 'copy', mp4_path]
            print(f"Converting {file_name} → {mp4_name} (lossless stream copy)")
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                # Provide ffmpeg's stderr for easier debugging when conversion fails
                print(f"Failed to convert {file_name}: {result.stderr.decode('utf-8')}")
                continue
        file_name_to_process = mp4_name
    else:
        file_name_to_process = file_name

    print(f"Processing: {file_name_to_process}")
    if source_url is None:
        result_path = colorizer.colorize_from_file_name(file_name_to_process, render_factor=render_factor)
    else:
        result_path = colorizer.colorize_from_url(source_url, file_name_to_process, render_factor=render_factor)

    # Keeping track of successful processing for logging purposes
    print(f"Processed: {file_name_to_process} → {result_path}")
