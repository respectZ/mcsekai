import json
import os
import sys


def hip_scale(file, multiplier=10):
    with open(file, "r") as f:
        data = json.load(f)

    # Get hip bones
    key = list(data["animations"].keys())[0]
    hip = data["animations"][key]["bones"]["hip"]

    # Loop each keyframe
    for keyframe in hip["position"]:
        # Loop each axis
        for axis in range(len(hip["position"][keyframe])):
            # Multiply the value by 10
            hip["position"][keyframe][axis] *= multiplier

    # Write the file
    with open(file, "w") as f:
        json.dump(data, f, indent=4)


def fix_empty(file):
    with open(file, "r") as f:
        data = json.load(f)

    # Get hip bones
    key = list(data["animations"].keys())[0]

    # Get bones
    bones = data["animations"][key]["bones"].keys()
    for bone in bones:
        # Get type of animation
        anim_types = list(data["animations"][key]["bones"][bone].keys())
        for anim_type in anim_types:
            # Remove if empty
            if not data["animations"][key]["bones"][bone][anim_type]:
                del data["animations"][key]["bones"][bone][anim_type]

    # Write the file
    with open(file, "w") as f:
        json.dump(data, f, indent=4)
