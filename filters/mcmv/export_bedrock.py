import json
import math
import os
from typing import Optional

from mcmv import utility
from mcmv.armature_formatter import MinecraftModelFormatter
from mcmv.armature_objects import ArmatureModel, MinecraftModel, DisplayVoxel, ArmatureAnimation, VisibleBone, PositionalBone
from mcmv.converter import Converter, RotationFixer
from mcmv.math_objects import Vector3, Euler, Quaternion


class BedrockUtility:

    @staticmethod
    def get_position_size(position: Vector3, size: Vector3) -> tuple[Vector3, Vector3]:
        position = BedrockUtility.get_geo_position(position)
        size = BedrockUtility.get_geo_position(size)

        for i in range(3):
            if size[i] < 0:
                shift = -size[i]
                size[i] = shift
                position[i] -= shift

        return position, size

    @staticmethod
    def get_geo_position(position: Vector3) -> Vector3:
        new_position = position * 16
        new_position.x *= -1
        return new_position

    @staticmethod
    def get_geo_position_no_scale(position: Vector3) -> Vector3:
        new_position = position.copy()
        new_position.x *= -1
        return new_position

    @staticmethod
    def get_geo_rotation(quaternion: Quaternion) -> Euler:
        rotation = Euler('zyx').set_from_quaternion(quaternion)
        rotation.x *= -1
        rotation.y *= -1

        return rotation

    @staticmethod
    def get_animation_position(position: Vector3) -> Vector3:
        new_position = position * 16
        new_position.x *= -1
        return new_position

    @staticmethod
    def get_rotation(quaternion: Quaternion) -> Euler:
        rotation = Euler('zyx').set_from_quaternion(quaternion)
        rotation.x *= -1
        rotation.y *= -1

        return rotation


class BedrockGeoFileFormatter:
    def __init__(self, format_version: str, identifier: str, texture_size: tuple[int, int],
                 visible_bounds_size: tuple[int, int] = (1, 2),
                 visible_bounds_offset: Vector3 = Vector3(0.0, 0.0, 0.0)):

        self.format_version = format_version
        self.identifier = identifier
        self.texture_size = texture_size
        self.visible_bounds_size = visible_bounds_size
        self.visible_bounds_offset = visible_bounds_offset

        self._bone_list = []
        self.model_no = ''

        self._json_info = {
            "format_version": self.format_version,
            "minecraft:geometry": [
                {
                    "description": {
                        "identifier": self.identifier,
                        "texture_width": self.texture_size[0],
                        "texture_height": self.texture_size[1],
                        "visible_bounds_width": self.visible_bounds_size[0],
                        "visible_bounds_height": self.visible_bounds_size[1],
                        "visible_bounds_offset": [
                            self.visible_bounds_offset.x,
                            self.visible_bounds_offset.y,
                            self.visible_bounds_offset.z
                        ]
                    },
                    "bones": self._bone_list
                }
            ]
        }

    def add_bone(self, name: str, parent_name: Optional[str], pivot: Vector3, rotation: Quaternion, display: DisplayVoxel):

        bone = {'name': utility.compatible_bone_name(name + self.model_no)}
        if parent_name is not None:
            bone['parent'] = utility.compatible_bone_name(
                parent_name + self.model_no)
        bone['pivot'] = list(BedrockUtility.get_geo_position(pivot).to_tuple())
        if rotation.x != 0 or rotation.y != 0 or rotation.z != 0:
            bone['rotation'] = list(rotation.to_tuple())
        if display is not None:
            bone['cubes'] = []
            origin, size = BedrockUtility.get_position_size(
                pivot + display.offset * (1 / 16), display.size * (1 / 16))

            cube_info = {
                'origin': list(origin.to_tuple()),
                'size': list(size.to_tuple()),
                'uv': [0, 0]
            }
            bone['cubes'].append(cube_info)

        self._bone_list.append(bone)

    def get_json_info(self):
        return self._json_info


class BedrockAnimFileFormatter:
    def __init__(self, format_version: str, identifier: str):
        self.format_version = format_version
        self.identifier = identifier

        self._bone_dict = {}
        self.model_no = ''

        self._json_info = {
            "format_version": format_version,
            "animations": {
                identifier: {
                    "animation_length": 0,
                    "bones": self._bone_dict
                }
            }
        }

        self.r = RotationFixer()

    def set_animation_length(self, length: float):
        self._json_info['animations'][self.identifier]['animation_length'] = length

    def add_keyframe(self, bone_name: str, time: float, position: Vector3 = None, rotation: Quaternion = None):
        bone_name = utility.compatible_bone_name(bone_name + self.model_no)
        if bone_name not in self._bone_dict:
            self._bone_dict[bone_name] = {'rotation': {}, 'position': {}}
        bone_info = self._bone_dict[bone_name]
        if position is not None:
            bedrock_position = BedrockUtility.get_animation_position(position)

            bone_info['position'][str(time)] = list(
                bedrock_position.to_tuple())

        if rotation is not None:
            bedrock_rotation = BedrockUtility.get_rotation(rotation)
            bedrock_rotation = self.r.fix_rotation(bone_name, bedrock_rotation)

            bone_info['rotation'][str(time)] = list(
                bedrock_rotation.to_tuple())

    def get_json_info(self):
        return self._json_info


class BedrockModelExporter:
    translation: Optional[dict[str, str]]
    minecraft_model: Optional[MinecraftModel]
    original_model: Optional[ArmatureModel]

    model_no: str

    def __init__(self):
        self.translation = None
        self.fps = 20
        self.minecraft_model = None
        self.original_model = None

    def set_model_info(self, model: ArmatureModel, minecraft_model: MinecraftModel, translation: dict[str, str] = None, model_no: str = ''):
        self.original_model = model.copy()
        self.minecraft_model = minecraft_model
        self.translation = translation

        self.model_no = model_no

    def write_geo_model(self, path: str, file_name: str, model_header: BedrockGeoFileFormatter,
                        offset: Vector3 = Vector3().copy(), rotate: Quaternion = Quaternion().copy()) -> None:
        """Write the bone information from self.minecraft_model to a .geo.json file."""
        model_header.model_no = self.model_no

        bones = self.minecraft_model.bones

        global_transformation = MinecraftModelFormatter.get_model_global(
            self.minecraft_model, offset)
        global_transformation[self.minecraft_model.root.name] = (
            global_transformation[self.minecraft_model.root.name][0], rotate)

        for bone_name in bones:
            bone = bones[bone_name]
            position, rotation = global_transformation[bone.name]

            if isinstance(bone, VisibleBone):
                display = bone.display
            else:
                display = None

            if bone.parent is not None:
                parent_name = bone.parent.name
            else:
                parent_name = None

            model_header.add_bone(bone.name, parent_name,
                                  position, rotation, display)

        complete_path = os.path.join(path, file_name + ".geo.json")
        open(complete_path, 'w').close()
        g = open(complete_path, "a", encoding="utf-8")
        # Write the header

        g.write(json.dumps(model_header.get_json_info(), ensure_ascii=False))

    def write_animation(self, path: str, file_name: str, model_header: BedrockAnimFileFormatter, animation: ArmatureAnimation):
        complete_path = os.path.join(path, file_name + ".animation.json")
        open(complete_path, 'w').close()
        g = open(complete_path, "a", encoding="utf-8")
        model_header.set_animation_length(
            math.ceil(len(animation.frames) / animation.fps))
        model_header.model_no = self.model_no

        for i, frame in enumerate(animation.frames):
            frame_time = i / animation.fps

            Converter.set_animation_frame(self.original_model, frame)
            Converter.set_minecraft_transformation(
                self.minecraft_model, self.original_model, self.translation)

            for bone_name in self.minecraft_model.bones:
                bone = self.minecraft_model.bones[bone_name]

                if bone is self.minecraft_model.root:
                    continue
                elif isinstance(bone, PositionalBone):
                    model_header.add_keyframe(
                        bone_name, frame_time, bone.local_animation_position, None)
                elif isinstance(bone, VisibleBone):
                    model_header.add_keyframe(
                        bone_name, frame_time, None, bone.local_animation_rotation)

        g.write(json.dumps(model_header.get_json_info(), ensure_ascii=False))
