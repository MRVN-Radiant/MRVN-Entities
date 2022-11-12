import fnmatch
import os

import pytest
import xmlschema


ent_schema = xmlschema.XMLSchema("schema/entity_definitions.xsd")

games = tuple(filter(os.path.isdir, os.listdir("mrvn")))

mrvn_xml = [os.path.join("mrvn", g, x) for g in games
            for x in fnmatch.filter(os.listdir(f"mrvn/{g}"), "*.xml")]

simulacrum_ent = [os.path.join("simulacrum", g, e) for g in games
                  for e in fnmatch.filter(os.listdir(f"simulacrum/{g}"), "*.ent")]


@pytest.mark.parametrize("xml_filename", (*mrvn_xml, *simulacrum_ent))
def validate(xml_filename: str):
    raise NotImplementedError()
