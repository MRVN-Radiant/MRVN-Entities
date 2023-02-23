import fnmatch
import json
import os
import re

import jsonschema
import pytest


games = tuple(filter(lambda p: os.path.isdir(os.path.join("mrvn", p)), os.listdir("mrvn")))

entity_schema = json.load(open("tests/schema/entity.json"))
entity_json = [os.path.join("pilot", g, j).replace("\\", "/") for g in games
               for j in fnmatch.filter(os.listdir(f"pilot/{g}"), "*.json")]

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
key_tests = {"string": r".*",
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
key_tests = {k: t if not isinstance(t, str) else (lambda v: re.match(t, v) is not None) for k, t in key_tests.items()}


@pytest.mark.parametrize("json_filename", entity_json)
def test_entity(json_filename: str):
    with open(json_filename) as json_file:
        entity = json.load(json_file)
    jsonschema.validate(entity, schema=entity_schema)
    # TODO: test choiceTypes are defined in either mrvn/*.xml or pilot/*/choiceTypes/*.json
    # TODO: verify any choiceType selections are valid


@pytest.mark.parametrize("json_filename", choiceType_json)
def test_choiceType(json_filename: str):
    with open(json_filename) as json_file:
        choiceType = json.load(json_file)
    jsonschema.validate(choiceType, schema=choiceType_schema)
    # TODO: enforce filename matches


blocks = json.load(open("blocks.json"))


@pytest.mark.parametrize("json_filename", entity_json)
def test_valid_entity_index(json_filename: str):
    with open(json_filename) as json_file:
        entity = json.load(json_file)
    game = json_filename.replace("\\", "/").split("/")[-2]
    assert entity["Entity"] in blocks[game][entity["Block"]], f"not in {entity['Block']}"
    # TODO: give the correct block in the assert message


# NOTE: pilot .json is allowed to add new keys & spawnflags
