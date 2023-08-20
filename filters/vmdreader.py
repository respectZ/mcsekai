import json
import os
import sys
import struct

HEADER_BYTE = 50
BONE_BYTE = 111
MORPH_BYTE = 23
CAMERA_BYTE = 61
LIGHT_BYTE = 28
SHADODW_BYTE = 9

# Read int from bytes and offset


def read_int(data, offset):
    return int.from_bytes(data[offset:offset+4], byteorder='little')

# Read float from bytes and offset


def read_float(data, offset):
    return float.from_bytes(data[offset:offset+4], byteorder='little')


def read_string(data, offset):
    string = ''
    while data[offset] != 0:
        string += chr(data[offset])
        offset += 1
    return string


def readUInt32LE(data, offset):
    return struct.unpack('<I', data[offset:offset+4])[0]


def readVector3LE(buffer, offset):
    x = struct.unpack("<f", buffer[offset + 0:offset + 4])[0]
    y = struct.unpack("<f", buffer[offset + 4:offset + 8])[0]
    z = struct.unpack("<f", buffer[offset + 8:offset + 12])[0]
    return [x, y, z]


def getBezierCamera(bezier):
    x = {
        "x1": bezier[0], "x2": bezier[1],
        "y1": bezier[2], "y2": bezier[3]
    }
    y = {
        "x1": bezier[4], "x2": bezier[5],
        "y1": bezier[6], "y2": bezier[7]
    }
    z = {
        "x1": bezier[8], "x2": bezier[9],
        "y1": bezier[10], "y2": bezier[11]
    }
    r = {
        "x1": bezier[12], "x2": bezier[13],
        "y1": bezier[14], "y2": bezier[15]
    }
    l = {
        "x1": bezier[16], "x2": bezier[17],
        "y1": bezier[18], "y2": bezier[19]
    }
    v = {
        "x1": bezier[20], "x2": bezier[21],
        "y1": bezier[22], "y2": bezier[23]
    }

    return {
        "x": x,
        "y": y,
        "z": z,
        "r": r,
        "l": l,
        "v": v
    }


def readVMD(path):
    with open(path, "rb") as f:
        data = f.read()

    # Check if 0 to 25 is "Vocaloid Motion Data 0002"
    if data[0:25] != b'Vocaloid Motion Data 0002':
        print("Not a valid VMD file")
        return

    reader = Reader()
    camera = reader.readCamera(data)
    return {
        "camera": camera
    }


def readCamera(path):
    with open(path, "rb") as f:
        data = f.read()

    # Check if 0 to 25 is "Vocaloid Motion Data 0002"
    if data[0:25] != b'Vocaloid Motion Data 0002':
        print("Not a valid VMD file")
        return

    reader = Reader()
    camera = reader.readCamera(data)
    return camera


class Reader:
    HEADER_BYTE = 50
    BONE_BYTE = 111
    MORPH_BYTE = 23
    CAMERA_BYTE = 61
    LIGHT_BYTE = 28
    SHADODW_BYTE = 9

    def readMeta(self, buffer):
        header = {}
        header["begin"] = 0
        header["byte"] = self.HEADER_BYTE
        header["signature"] = 30
        header["name"] = 20
        header["total"] = 50
        begin = header["begin"] + (header["byte"] * 1)

        bone = {}
        bone["count"] = readUInt32LE(buffer, begin)
        bone["begin"] = begin + 4
        bone["byte"] = self.BONE_BYTE
        bone["total"] = bone["byte"] * bone["count"]
        begin = bone["begin"] + (bone["byte"] * bone["count"])

        morph = {}
        morph["count"] = readUInt32LE(buffer, begin)
        morph["begin"] = begin + 4
        morph["byte"] = self.MORPH_BYTE
        morph["total"] = morph["byte"] * morph["count"]
        begin = morph["begin"] + (morph["byte"] * morph["count"])

        camera = {}
        camera["count"] = readUInt32LE(buffer, begin)
        camera["begin"] = begin + 4
        camera["byte"] = self.CAMERA_BYTE
        camera["total"] = camera["byte"] * camera["count"]
        begin = camera["begin"] + (camera["byte"] * camera["count"])

        light = None
        if len(buffer) > begin:
            light = {}
            light["count"] = readUInt32LE(buffer, begin)
            light["begin"] = begin + 4
            light["byte"] = self.LIGHT_BYTE
            light["total"] = light["byte"] * light["count"]
            if len(buffer) < light["begin"] + light["total"]:
                light = None

        begin = light["begin"] + \
            (light["byte"] * light["count"]) if light else None

        shadow = None
        if len(buffer) > begin:
            shadow = {}
            shadow["count"] = readUInt32LE(buffer, begin)
            shadow["begin"] = begin + 4
            shadow["byte"] = self.SHADODW_BYTE
            shadow["total"] = shadow["byte"] * shadow["count"]
            if len(buffer) < shadow["begin"] + shadow["total"]:
                shadow = None

        begin = shadow["begin"] + \
            (shadow["byte"] * shadow["count"]) if shadow else None

        ik = None
        if len(buffer) > begin:
            ik = {}
            ik["count"] = readUInt32LE(buffer, begin)
            ik["begin"] = begin + 4
            ik["number"] = readUInt32LE(buffer,
                                        begin + 4 + 5) if ik["count"] > 0 else 0
            ik["byte"] = 9 + 21 * ik["number"]
            ik["total"] = ik["byte"] * ik["count"]
            if len(buffer) < ik["begin"] + ik["total"]:
                ik = None

        return {
            "header": header,
            "bone": bone,
            "morph": morph,
            "camera": camera,
            "light": light,
            "shadow": shadow,
            "ik": ik
        }

    def readCamera(self, buffer):
        meta = self.readMeta(buffer)["camera"]
        if meta is None:
            return []

        results = []
        for i in range(meta["count"]):
            begin = meta["begin"] + (meta["byte"] * i)
            j = 0
            frame = readUInt32LE(buffer, begin + j)
            j += 4
            length = (struct.unpack(
                "<f", buffer[begin + j:begin + j + 4])[0]) * -1
            j += 4
            location = readVector3LE(buffer, begin + j)
            j += 12
            rotation = readVector3LE(buffer, begin + j)
            rotation[0] *= -1
            j += 12
            bezier = getBezierCamera(buffer[begin + j:begin + j + 24])
            j += 24
            viewAngle = readUInt32LE(buffer, begin + j)
            j += 4
            perspective = (struct.unpack(
                "<B", buffer[begin + j:begin + j + 1])[0]) == 0
            j += 1
            results.append({
                "frame": frame,
                "length": length,
                "location": location,
                "rotation": rotation,
                "bezier": bezier,
                "viewAngle": viewAngle,
                "perspective": perspective
            })
        return results


# Read args
if __name__ == "__main__":
    args = sys.argv
    if len(args) < 2:
        print("Usage: python vmdreader.py <path>")
        exit(1)

    # Read VMD
    readVMD(args[1])
