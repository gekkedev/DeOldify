#NOTE: This must be the first call in order for the script to work properly
from deoldify import device
# Automatically select the best available device
# (CUDA, DirectML, or CPU) using internal heuristics
#choices when setting it manually:  CPU, GPU0...GPU7
#device.set(device=DeviceId.GPU0)

import torch
from deoldify.visualize import *
plt.style.use('dark_background')
import warnings
warnings.filterwarnings("ignore", category=UserWarning, message=".*?Your .*? set is empty.*?")

print("Loading video colorizer...")
colorizer = get_video_colorizer()
print("Video colorizer loaded.")

# Example video: https://twitter.com/silentmoviegifs/status/1116751583386034176

# read and process the entire video folder: ./video/source/[file_names]
import os, subprocess
from fastprogress.fastprogress import master_bar

folder_path = 'video/source'
result_path = None
directory = os.listdir(folder_path)
mb = master_bar(directory)
for file_name in mb:
    mb.main_bar.comment = file_name
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

    # NOTE:  Max is 44 with 11GB video cards.  21 is a good default
    # render_factor = 21
    # if set manually, provide as param to the video colorizer like this: render_factor=render_factor

    mb.write(f"Processing: {file_name_to_process}")
    # watermark disabled because too blurry on small resolution videos (IDEA: implement scaling)
    result_path = colorizer.colorize_from_file_name(file_name_to_process, watermarked=False, bar=mb)

    # Keeping track of successful processing for logging purposes
    print(f"Processed: {file_name_to_process} → {result_path}")
