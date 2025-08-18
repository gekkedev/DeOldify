# NOTE: This must be the first call in order to work properly!
from deoldify import device, guess_render_factor
from deoldify.device_id import DeviceId
#choices:  CPU, GPU0...GPU7
device.set(device=DeviceId.GPU0)

import torch
print("CUDA available: " + str(torch.cuda.is_available()))

from deoldify.visualize import *
plt.style.use('dark_background')
import warnings
warnings.filterwarnings("ignore", category=UserWarning, message=".*?Your .*? set is empty.*?")

print("Loading video colorizer...")
colorizer = get_video_colorizer()
print("Video colorizer loaded.")

# NOTE: Make source_url None to just read from file at ./video/source/[file_name] directly without modification
source_url = None
#source_url='https://twitter.com/silentmoviegifs/status/1116751583386034176'

# read and process the entire video folder
import os
import subprocess
folder_path = 'video/source'
result_path = None
subject_type = "landscape"
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

    # Extract a single frame to estimate a good render_factor.
    base, _ = os.path.splitext(file_name_to_process)
    frame_path = os.path.join(folder_path, f"{base}_frame0.jpg")
    cmd = [
        'ffmpeg',
        '-y',
        '-i', os.path.join(folder_path, file_name_to_process),
        '-frames:v', '1',
        frame_path,
    ]
    frame_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if frame_result.returncode == 0:
        render_factor = guess_render_factor(frame_path, subject_type=subject_type)
        os.remove(frame_path)
    else:
        print(f"Failed to extract frame for {file_name_to_process}: {frame_result.stderr.decode('utf-8')}")
        # NOTE:  Max is 44 with 11GB video cards.  21 is a good default
        render_factor = 21  # reasonable fallback

    print(f"Processing: {file_name_to_process} (render_factor={render_factor})")
    if source_url is None:
        result_path = colorizer.colorize_from_file_name(file_name_to_process, render_factor=render_factor)
    else:
        result_path = colorizer.colorize_from_url(source_url, file_name_to_process, render_factor=render_factor)

    # Keeping track of successful processing for logging purposes
    print(f"Processed: {file_name_to_process} → {result_path}")
