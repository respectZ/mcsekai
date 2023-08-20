from mcmv.armature_formatter import MinecraftModelCreator
from mcmv.armature_objects import DisplayVoxel
from mcmv.export_bedrock import BedrockModelExporter, BedrockGeoFileFormatter, BedrockAnimFileFormatter
from mcmv.export_java import JavaModelExporter
from mcmv.import_file import BvhFileLoader
from mcmv.math_objects import Vector3, Quaternion, Euler
import sys
import json
import os

import mcmv_scale
import camera as cam

translation = {
    "root": "Body",
    "hip": "Hip",
    "body": "Chest",
    "head": "Head",
    "elbow_l": "Right_Elbow",
    "wrist_l": "Right_ForeArmRoll",
    "knee_l": "Right_Knee",
    "ankle_l": "Right_Ankle",
    "elbow_r": "Left_Elbow",
    "wrist_r": "Left_ForeArmRoll",
    "knee_r": "Left_Knee",
    "ankle_r": "Left_Ankle",
}
bone_list = [
    ('body',
     'head',
     Vector3(0.0, 8.0, 0.0),
     Vector3(0.0, 0.0, 0.0),
     DisplayVoxel(Vector3(-4.0, 0.0, -4.0), Vector3(8.0, 8.0, 8.0),
                  'diamond_hoe{CustomModelData:100}')
     ),
    ('hip',
     'body',
        Vector3(0.0, 12.0, 0.0),
        Vector3(0.0, 0.0, 0.0),
        DisplayVoxel(Vector3(-4.0, 0.0, -2.0), Vector3(8.0, 12.0, 4.0),
                     'diamond_hoe{CustomModelData:101}')
     ),
    ('body',
     'elbow_r',
        Vector3(0.0, -5.0, 0.0),
        Vector3(4.0, -1.0, 0.0),
        DisplayVoxel(Vector3(0.0, -5.0, -2.0), Vector3(4.0, 6.0, 4.0),
                     'diamond_hoe{CustomModelData:102}')
     ),
    ('elbow_r',
     'wrist_r',
        Vector3(0.0, -4.0, 0.0),
        Vector3(2.0, 0.0, 0.0),
        DisplayVoxel(Vector3(-2.0, -6.0, -2.0), Vector3(4.0, 6.0, 4.0),
                     'diamond_hoe{CustomModelData:103}')
        # )
     ),
    ('body',
     'elbow_l',
        Vector3(0.0, -5.0, 0.0),
        Vector3(-4.0, -1.0, 0.0),
        DisplayVoxel(Vector3(-4.0, -5.0, -2.0), Vector3(4.0, 6.0, 4.0),
                     'diamond_hoe{CustomModelData:104}')
     ),
    ('elbow_l',
     'wrist_l',
        Vector3(0.0, -4.0, 0.0),
        Vector3(-2.0, 0.0, 0.0),
        DisplayVoxel(Vector3(-2.0, -6.0, -2.0), Vector3(4.0, 6.0, 4.0),
                     'diamond_hoe{CustomModelData:105}')
        # )
     ),
    ('body',
     'knee_r',
        Vector3(0.0, -6.0, 0.0),
        Vector3(2.0, -12.0, 0.0),
        DisplayVoxel(Vector3(-2.0, -6.0, -2.0), Vector3(4.0, 6.0, 4.0),
                     'diamond_hoe{CustomModelData:106}')
     ),
    ('knee_r',
     'ankle_r',
        Vector3(0.0, -6.0, 0.0),
        Vector3(0.0, 0.0, -2.0),
        DisplayVoxel(Vector3(-2.0, -6.0, 0.0), Vector3(4.0, 6.0, 4.0),
                     'diamond_hoe{CustomModelData:107}')
     ),
    ('body',
     'knee_l',
        Vector3(0.0, -6.0, 0.0),
        Vector3(-2.0, -12.0, 0.0),
        DisplayVoxel(Vector3(-2.0, -6.0, -2.0), Vector3(4.0, 6.0, 4.0),
                     'diamond_hoe{CustomModelData:108}')
     ),
    ('knee_l',
     'ankle_l',
        Vector3(0.0, -6.0, 0.0),
        Vector3(0.0, 0.0, -2.0),
        DisplayVoxel(Vector3(-2.0, -6.0, 0.0), Vector3(4.0, 6.0, 4.0),
                     'diamond_hoe{CustomModelData:109}')
     ),
    (
        'root',
        'hip'
    )
]


def generate(src, song_name=""):
    # Get filename
    filename = src.split('/')[-1].split('.')[0]

    file_loader = BvhFileLoader(src, scale=0.1, order='xyz',
                                face_north=Quaternion().set_from_euler(Euler('xyz', 0.0, 0.0, 0.0)))
    model = file_loader.get_model()
    animation = file_loader.get_animation()

    m = MinecraftModelCreator()
    m.set_bones(bone_list)

    b = BedrockModelExporter()
    b.set_model_info(model, m.minecraft_model, translation)
    # Make directory
    dir = f"./RP/animations/songs/{song_name}/"
    if not os.path.exists(dir):
        os.makedirs(dir)
    b.write_animation(dir, f"{filename}",
                      BedrockAnimFileFormatter('1.8.0', f"animation.{song_name}.{filename}"), animation)
    # Scale animation
    mcmv_scale.fix_empty(dir + f"{filename}.animation.json")
    mcmv_scale.hip_scale(dir + f"{filename}.animation.json", 20)


# Check if has args
print(sys.argv)
if len(sys.argv) > 1:
    data = json.loads(sys.argv[1])
    for song in data["songs"].keys():
        path = data["songs"][song]["path"]
        for file in os.listdir(path):
            if file.endswith(".bvh"):
                print(f"[INFO] Generating {file} for {song}")
                generate(os.path.join(path, file), song)
            if file.endswith(".vmd"):
                print("VMD!")
                cam.convert(os.path.join(path, file), song)
