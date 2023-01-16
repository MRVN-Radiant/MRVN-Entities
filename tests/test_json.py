import fnmatch
import json
import os

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


@pytest.mark.parametrize("json_filename", entity_json)
def test_entity(json_filename: str):
    with open(json_filename) as json_file:
        entity = json.load(json_file)
    jsonschema.validate(entity, schema=entity_schema)
    # TODO: dynamic type checking
    # -- list of valid key types for radiant
    # -- add choiceType lists from .xml & .json


@pytest.mark.parametrize("json_filename", choiceType_json)
def test_choiceType(json_filename: str):
    with open(json_filename) as json_file:
        choiceType = json.load(json_file)
    jsonschema.validate(choiceType, schema=choiceType_schema)


blocks = json.load(open("blocks.json"))


@pytest.mark.parametrize("json_filename", entity_json)
def test_valid_entity_index(json_filename: str):
    with open(json_filename) as json_file:
        entity = json.load(json_file)
    game = json_filename.replace("\\", "/").split("/")[-2]
    assert entity["Entity"] in blocks[game][entity["Block"]], f"not in {entity['Block']}"
    # TODO: give the correct block in the assert message


# NOTE: pilot .json is allowed to add new keys & spawnflags
