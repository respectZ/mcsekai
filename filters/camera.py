import json
import os
import sys
import math
import vmdreader as vmdr


def convert(path, song=""):
    camera = vmdr.readCamera(path)
    frames = {}
    cmds = []
    skip_easing = False
    for i in range(len(camera)):
        frame = camera[i]["frame"]
        tick = math.floor((frame / 30) * 20)

        # Check for skip easing
        if i > 0 and i < len(camera) - 1:
            if camera[i - 1]["frame"] - camera[i]["frame"] == -1:
                skip_easing = True

        if tick in frames:
            continue
        frames[tick] = True

        D = (camera[i]["viewAngle"] - 26) / 1.2
        D = 0

        location = camera[i]["location"]
        rotation = camera[i]["rotation"]

        S = 1 / 6  # was 7.2

        # Rescale
        for j in range(3):
            location[j] *= S
            # Convert to degree
            rotation[j] *= (180 / math.pi)

        rotation[1] *= -1

        x, y, z = location
        x *= -1
        rotX, rotY, rotZ = rotation

        # x, y, z = rotate_3d_euler(x, y, z, rotX, rotY, 0)

        # Manual x2 y2 z2
        x2 = math.sin(math.radians(rotY)) * math.cos(math.radians(rotX)) * -D
        y2 = math.sin(math.radians(rotX)) * -D
        z2 = math.cos(math.radians(rotY)) * math.cos(math.radians(rotX)) * -D

        # Sum
        x += x2
        y += y2
        z += z2

        # cmd = f"execute as @a if score @s villain matches {tick + 1} positioned as @e[type=pj:song_manager,c=1] rotated as @e[type=pj:song_manager,c=1] positioned ~~~ positioned ^^^10 run camera @s set minecraft:free ease 0.1 linear pos ~{x}~{y}~{z} rot ~{rotX:f}~{rotY:f}"
        cmd = f"execute as @a if score @s {song} matches {tick + 1} positioned as @e[type=pj:song_manager,c=1] rotated as @e[type=pj:song_manager,c=1] positioned ~~-0.8~ positioned ^^^9 positioned ~{x:f}~{y:f}~{z:f} rotated ~{rotX:f} ~{rotY:f} run camera @s set minecraft:free ease 0.1 linear pos ^^^ rot {rotX:f} {rotY:f}"
        if skip_easing:
            skip_easing = False
            cmd = cmd.replace("ease 0.1 linear", "")
        cmds.append(cmd)

    fr = list(frames.keys())[-1]
    for j in range(fr + 1, 0, -1):
        cmd = f"execute as @a if score @s {song} matches {j} run scoreboard players set @s {song} {j + 1}"
        cmds.append(cmd)

    cmds = "\n".join(cmds)
    os.makedirs(f"./BP/functions/songs/{song}", exist_ok=True)
    with open(f"./BP/functions/songs/{song}/camera.mcfunction", "w") as f:
        f.write(cmds)


# convert("./data/mcmv/villain/camera.vmd", "villain")
