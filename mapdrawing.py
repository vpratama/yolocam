import json
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import os
import numpy as np

video_folder = 'video'
json_files = [f for f in os.listdir(video_folder) if f.endswith('.json')]

json_data = "[" + "".join([open(os.path.join(video_folder, f), 'r').read() for f in json_files]) + "]"

json_obj = json.loads(json_data)

for data in json_obj:
    fig, ax = plt.subplots()
    ax.add_patch(Rectangle((data["x1"], data["y1"]), data["x2"]-data["x1"], data["y2"]-data["y1"], fill=False, linewidth=2, color='r'))
    ax.set_xlim(0, 1500)
    ax.set_ylim(0, 1000)
    ax.text(data["x1"], data["y1"], f'{data["name"]} ({data["confidence"]:.2f})', color='r', bbox=dict(facecolor='white', alpha=0.5))
    plt.show()