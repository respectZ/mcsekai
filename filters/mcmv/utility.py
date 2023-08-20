import random
from typing import Optional


def compatible_bone_name(name: str) -> str:
    return name.replace(' ', '_').replace('.', '_').replace(':', '_').replace('/', '_')


def tuple_to_m_list(tup: tuple, c: str = '') -> str:
    """Return a string representation of a tuple to be used as an NBT list in Minecraft."""
    if type(tup[0]) is float:
        return '[' + ', '.join(tuple('{:f}'.format(i) + c for i in tup)) + ']'
    else:
        return '[' + ', '.join(tuple(str(i) + c for i in tup)) + ']'


def uuid_str_to_uuid_nbt(uuid: str) -> str:
    """Return a string representation of a integer list UUID-format converted from a normal UUID format."""
    split_uuid = uuid.split('-')
    a = split_uuid[0]
    b = split_uuid[1] + split_uuid[2]
    c = split_uuid[3] + split_uuid[4][0:4]
    d = split_uuid[4][4:16]
    uuids = tuple(str((int(i, 16) + 2147483648) % 4294967296 - 2147483648) for i in (a, b, c, d))
    return 'UUID:[I;' + ','.join(uuids) + ']'


def uuid_ints_to_uuid_str(uuid: tuple[int, int, int, int]):
    """Return a string representation given the 4 integer UUID representation."""
    usc = tuple(hex(i % 2 ** 32)[2:10].zfill(8) for i in uuid)

    return '-'.join([usc[0], usc[1][0:4], usc[1][4:8], usc[2][0:4], usc[2][4:8] + usc[3]])


def get_function_directory(directory: str, file: Optional[str]) -> str:
    """Return a function directory  from the directory and file that Minecraft uses to look up functions."""
    directory_list = directory.split('/')
    if directory_list[-1] == '':
        directory_list.pop()

    for i in range(len(directory_list)):
        if directory_list[i] == 'data':
            if directory_list[i - 2] == 'datapacks' and directory_list[i + 2] == 'functions':
                datapack_name = directory_list[i + 1]
                datapack_directory = directory_list[i + 3:len(directory_list)]
                if file is None:
                    return datapack_name + ':' + '/'.join(datapack_directory)
                else:
                    datapack_directory.append('')
                    return datapack_name + ':' + '/'.join(datapack_directory) + file
    print('This doesn\'t seem to be a valid path!')
    raise 'Incorrect Path!'


def get_joint_uuids(function_directory: str, function_name: str, name: str) -> tuple[str, str]:
    """Uses the function_directory, function_name, and name to create UUIDs for the AEC-Stand pair."""

    random.seed(get_function_directory(function_directory, function_name) + name)

    # noinspection PyTypeChecker
    aec_uuid = uuid_ints_to_uuid_str(tuple(random.randint(-2 ** 31, 2 ** 31 - 1) for _ in range(4)))
    # noinspection PyTypeChecker
    stand_uuid = uuid_ints_to_uuid_str(tuple(random.randint(-2 ** 31, 2 ** 31 - 1) for _ in range(4)))

    return aec_uuid, stand_uuid
