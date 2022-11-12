import fnmatch
import json
import os

import jsonschema
import pytest


games = tuple(filter(os.path.isdir, os.listdir("mrvn")))

entity_schema = json.load("schema/entity.json")
entity_json = [os.path.join("pilot", g, j) for g in games
               for j in fnmatch.filter(os.listdir(f"pilot/{g}"), "*.json")]

choiceType_schema = json.load("schema/choiceType.json")
choiceType_json = list()
for game_dir in games:
    search_dir = os.path.join("pilot", game_dir, "choiceTypes")
    if not os.path.exists(search_dir):
        continue
    for choiceType in fnmatch.filter(os.listdir(search_dir), "*.json"):
        choiceType_json.append()


@pytest.mark.parametrize("json_filename", entity_json)
def validate_entity(json_filename: str):
    entity = json.load(json_filename)
    jsonschema.validate(entity, schema=entity_schema)
    # TODO: dynamic type checking
    # -- list of valid key types for radiant
    # -- add choiceType lists from .xml & .json


@pytest.mark.parametrize("json_filename", choiceType_json)
def validate_choiceType(json_filename: str):
    choiceType = json.load(json_filename)
    jsonschema.validate(choiceType, schema=choiceType_schema)
