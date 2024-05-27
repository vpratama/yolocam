import json
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import os
import numpy as np

# Define the conversion factor
conversion_factor = 0.026458333 # This value is used when the pixel density is 96 dpi

video_folder = 'video'
json_files = [f for f in os.listdir(video_folder) if f.endswith('.json')]

json_data = "[" + "".join([open(os.path.join(video_folder, f), 'r').read() for f in json_files]) + "]"

json_obj = json.loads(json_data)

for data in json_obj:
    # Calculate the differences between the x-coordinates and the y-coordinates
    dx = data["x2"] - data["x1"]
    dy = data["y2"] - data["y1"]

    # Calculate the distance between the two points using the Pythagorean theorem
    distance = np.sqrt(dx**2 + dy**2)

    # Convert the distance from pixels to centimeters
    distance_cm = distance * conversion_factor

    fig, ax = plt.subplots()
    ax.add_patch(Rectangle((data["x1"], data["y1"]), data["x2"]-data["x1"], data["y2"]-data["y1"], fill=False, linewidth=2, color='r'))
    ax.set_xlim(0, 1500)
    ax.set_ylim(0, 1000)
    ax.text(data["x1"], data["y1"], f'{data["name"]} ({data["confidence"]:.2f}) Distance: {distance_cm:.2f} cm', color='r', bbox=dict(facecolor='white', alpha=0.5))
    plt.show()