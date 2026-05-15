import fnmatch
import json
import os
import re

import jsonschema
import pytest


games = [
    game
    for game in os.listdir("mrvn/")
    if os.path.isdir(os.path.join("mrvn", game))]

entity_schema = json.load(open("tests/schema/entity.json"))

entity_json = [
    os.path.join("pilot", game, filename).replace("\\", "/")
    for game in games
    for filename in fnmatch.filter(
        os.listdir(f"pilot/{game}"), "*.json")]

choiceType_schema = json.load(open("tests/schema/choiceType.json"))

choiceType_json = list()
for game_dir in games:
    search_dir = os.path.join("pilot", game_dir, "choiceTypes")
    if not os.path.exists(search_dir):
        continue
    for choiceType in fnmatch.filter(os.listdir(search_dir), "*.json"):
        choiceType_json.append(os.path.join(search_dir, choiceType).replace("\\", "/"))


def valid_conversion(value: str, func, count: int) -> bool:
    try:
        test = [float(a) for a in value.split()]
    except ValueError:
        return False
    return len(test) == count


# TODO: verify keyvalues
# https://github.com/MRVN-Radiant/MRVN-Radiant/blob/main/radiant/eclass_xml.cpp#L49-L68
key_tests = {
    "string": r".*",
    "array": r"[^;]*|([^;];)*[^;]+",
    "integer": lambda v: valid_conversion(v, int, 1),
    "boolean": r"0|1",
    # floats
    "real": lambda v: valid_conversion(v, float, 1),
    "angle": lambda v: valid_conversion(v, float, 3),
    "direction": lambda v: valid_conversion(v, float, 3),  # + range check?
    "real3": lambda v: valid_conversion(v, float, 3),
    "angles": lambda v: valid_conversion(v, float, 3),  # + range check?
    "color": lambda v: valid_conversion(v, float, 3),  # + range check?
    # identifiers
    "target": r".*",
    "targetname": r".*",
    # paths
    "sound": r".*",
    "texture": r".*",
    "model": r".*",
    "skin": r".*"}
# ^ {"keyName": test_func or r"test regex"}


key_tests = {
    key: test if not isinstance(test, str) else (lambda val: re.match(test, val) is not None)
    for key, test in key_tests.items()}


@pytest.mark.parametrize("json_filename", entity_json)
def test_entity(json_filename: str):
    with open(json_filename) as json_file:
        entity = json.load(json_file)
    filename_ext = os.path.basename(json_filename)
    filename = os.path.splitext(filename_ext)[0]
    assert filename == entity["Entity"], f"{entity['Entity']} defined in {filename_ext}"
    jsonschema.validate(entity, schema=entity_schema)
    # TODO: test choiceTypes are defined in either mrvn/*.xml or pilot/*/choiceTypes/*.json
    # TODO: verify any choiceType selections are valid


@pytest.mark.parametrize("json_filename", choiceType_json)
def test_choiceType(json_filename: str):
    with open(json_filename) as json_file:
        choiceType = json.load(json_file)
    filename_ext = os.path.basename(json_filename)
    filename = os.path.splitext(filename_ext)[0]
    assert filename == choiceType["Name"], f"{choiceType['Name']} defined in {filename_ext}"
    jsonschema.validate(choiceType, schema=choiceType_schema)


blocks = json.load(open("blocks.json"))


@pytest.mark.parametrize("json_filename", entity_json)
def test_valid_entity_index(json_filename: str):
    game = json_filename.replace("\\", "/").split("/")[-2]
    with open(json_filename) as json_file:
        entity = json.load(json_file)
    classname = entity["Entity"]
    entity_blocks = [
        block
        for block, classnames in blocks[game].items()
        if classname in classnames]
    assert len(entity_blocks) == 1, "couldn't determine entity's block"
    entity_block = entity_blocks[0]
    assert entity["Block"] == entity_block, "incorrect entity Block"
    # NOTE: we could automate setting entity blocks
    # -- but explicity stating the block in the .json is useful


# NOTE: pilot .json is allowed to add new keys & spawnflags
