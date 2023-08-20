import os
import json
import sys

# By default, the songs are from "./RP/animations/songs/"

songs = os.listdir("./RP/animations/songs/")

song_dict = {
    "hitorinbo_envy": 74,
    "villain": 170,
}


def inject_rp(entity_path):
    with open(entity_path, "r") as f:
        data = json.load(f)

    # Loop songs
    for song in songs:
        # Get song animations
        song_animations = [x.split(".")[0] for x in os.listdir(
            f"./RP/animations/songs/{song}/")]

        # Convert to dict, so will be: {"song.song_animation": "song_animation"}
        song_animations = {
            f"{song}.{x}": f"animation.{song}.{x}" for x in song_animations}

        data["minecraft:client_entity"]["description"]["animations"].update(
            song_animations)

    # Write the file
    with open(entity_path, "w") as f:
        json.dump(data, f, indent=4)


def inject_bp(entity_path):
    # Inject bp events
    for k, v in song_dict.items():
        inject_bp_events(entity_path, {
            f"song:{k}": {
                "set_property": {
                    "pj:song": v
                }
            }
        })


def inject_bp_events(entity_path, event):
    with open(entity_path, "r") as f:
        data = json.load(f)

    data["minecraft:entity"]["events"].update(event)

    with open(entity_path, "w") as f:
        json.dump(data, f, indent=4)


def generate_ac():
    ac_path = "./RP/animation_controllers/songs.ac.json"
    with open(ac_path, "r") as f:
        data = json.load(f)

    for song in songs:
        song_animations = [x.split(".")[0] for x in os.listdir(
            f"./RP/animations/songs/{song}/")]

        song_id = song_dict[song]

        # Create state
        data["animation_controllers"]["controller.animation.songs"]["states"][song] = {
            "transitions": [
                {
                    f"{song}.{x}": f"q.property('pj:song_ch') == {int(x)}"
                } for x in song_animations
            ] + [
                {
                    "default": f"q.property('pj:song_ch') != {song_id}"
                }
            ]
        }

        # Add to default
        data["animation_controllers"]["controller.animation.songs"]["states"]["default"]["transitions"].append(
            {
                song: f"q.property('pj:song') == {song_id}"
            }
        )

        # Create for every song_anims
        for song_animation in song_animations:
            data["animation_controllers"]["controller.animation.songs"]["states"][f"{song}.{song_animation}"] = {
                "animations": [
                    f"{song}.{song_animation}",
                    "fix"
                ],
                "transitions": [
                    {
                        "default": f"q.property('pj:song') != {song_id}"
                    }
                ]
            }

    # Write the file
    with open(ac_path, "w") as f:
        json.dump(data, f, indent=4)


# Check if has args
print(sys.argv)
if len(sys.argv) > 1:
    data = json.loads(sys.argv[1])
    for entity_dir in data["entities"]:
        for entity in os.listdir(f"./RP/entity/{entity_dir}/"):
            inject_rp(f"./RP/entity/{entity_dir}/{entity}")
        for entity in os.listdir(f"./BP/entities/{entity_dir}/"):
            inject_bp(f"./BP/entities/{entity_dir}/{entity}")

generate_ac()
