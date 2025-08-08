#NOTE:  This must be the first call in order to work properly!
from deoldify import device
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

#NOTE:  Max is 44 with 11GB video cards.  21 is a good default
render_factor=21
#NOTE:  Make source_url None to just read from file at ./video/source/[file_name] directly without modification
source_url = None
#source_url='https://twitter.com/silentmoviegifs/status/1116751583386034176'

# read and process the entire video folder
import os
folder_path = 'video/source'
result_path = None
for file_name in os.listdir(folder_path):
    file_path = os.path.join(folder_path, file_name)

    # Skip if not a file or not mp4 (uncertain if other formats are supported)
    if not os.path.isfile(file_path) or not file_name.lower().endswith('.mp4'):
        print(f"Skipping: {file_name} (not a valid mp4 file)")
        continue

    print(f"Processing: {file_name}")
    if source_url is None:
        result_path = colorizer.colorize_from_file_name(file_name, render_factor=render_factor)
    else:
        result_path = colorizer.colorize_from_url(source_url, file_name, render_factor=render_factor)

    print(f"Processed: {file_name} → {result_path}")