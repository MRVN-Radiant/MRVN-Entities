import fnmatch
import json
import os
from xml.etree import ElementTree

import pytest
# import xmlschema


# ent_schema = xmlschema.XMLSchema("tests/schema/entity_definitions.xsd")

games = [
    game
    for game in os.listdir("mrvn/")
    if os.path.isdir(os.path.join("mrvn", game))]

mrvn_xml = [
    os.path.join("mrvn", game, filename)
    for game in games
    for filename in fnmatch.filter(
        os.listdir(f"mrvn/{game}"), "*.xml")]

simulacrum_ent = [
    os.path.join("simulacrum", game, filename)
    for game in games
    for filename in fnmatch.filter(
        os.listdir(f"simulacrum/{game}"), "*.ent")]


# @pytest.mark.parametrize("xml_filename", (*mrvn_xml, *simulacrum_ent))
# def test_entity_definitions(xml_filename: str):
#     ent_schema.validate(xml_filename)


blocks = json.load(open("blocks.json"))
exclude = {
    game: {block: set() for block in blocks[game]}
    for game in blocks}
# exclude new & unused entities
exclude["r2"]["ENTITIES_script"].update({
    "mp_weapon_rspn101_og", "mp_weapon_wingman_n", "mp_weapon_grenade_sonar"})


@pytest.mark.parametrize("game,xml_block", [(g, b) for g in blocks for b in blocks[g] if b != "radiant"])
def test_coverage(game: str, xml_block: str):
    xml = ElementTree.parse(f"mrvn/{game}/{xml_block}.xml")
    expected = set(blocks[game][xml_block])
    expected.difference_update(exclude[game][xml_block])
    written = {e.get("name") for e in xml.getroot() if e.tag in ("point", "group")}
    assert expected.difference(written) == set(), "some entity classes were not written"
    assert written.difference(expected) == set(), "bsp entity not listed in blocks.json"
