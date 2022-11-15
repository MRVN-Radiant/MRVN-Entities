import collections
import fnmatch
import json
import os
import sys
from xml.dom import minidom

if not sys.argv != (sys.argv[0], "--unsafe"):
    unsafe = False
    import xmlschema  # noqa F401
    import jsonschema  # noqa F401
    # TODO: pre-load schemas from tests/schema
else:
    unsafe = True
    # TODO: UserWarning


ent_filename = {"ENTITIES.xml": "entities.ent",
                "ENTITIES_env.xml": "environment_entites.ent",
                "ENTITIES_fx.xml": "effects_entities.ent",
                "ENTITIES_script.xml": "script_entities.ent",
                "ENTITIES_spawn.xml": "spawn_entities.ent",
                "ENTITIES_snd.xml": "sound_entities.ent"}

types = {"float": "real"}  # fuzzy matching
defaults = {"float": "1.0"}  # allow undefined
# NOTE: choiceTypes should default to first Option


if __name__ == "__main__":
    for game in filter(lambda p: os.path.isdir(os.path.join("mrvn", p)), os.listdir("mrvn")):
        print(f"processing mrvn/{game}/")
        in_dir = os.path.join("mrvn", game)
        out_dir = os.path.join("simulacrum", game)
        os.makedirs(out_dir, exist_ok=True)

        print(f"gathering overrides from pilot/{game}/")
        json_dir = os.path.join("pilot", game)
        assert os.path.exists(json_dir)

        choiceTypes = set()
        # ^ {"ChoiceType"}
        # TODO: if not unsafe: verify choiceType["Name"] == filename
        # -- warn if any go unused

        ent_overrides = collections.defaultdict(set)
        # ^ {"ENTITIES.xml": {"entity.json"}}
        for json_filename in fnmatch.filter(os.listdir(json_dir), "*.json"):
            try:
                with open(os.path.join(json_dir, json_filename)) as json_file:
                    entity = json.load(json_file)
            except Exception as exc:
                print(f"{json_filename} broke ({exc.__name__})")
                # raise exc
            # TODO:
            # if safe:  # copy of tests.test_json.validate()
            #     assert jsonschema.is_valid(entity)
            #     assert entity["Entity"] in blocks[entity["Block"]]
            #     # TODO: validate type defaults
            ent_overrides[f"{entity['Block']}.xml"].add(json_filename)
        print(f"collected {sum(map(len, ent_overrides.values()))} entities across {len(ent_overrides)} blocks")

        for xml_filename in fnmatch.filter(os.listdir(in_dir), "*.xml"):
            print(f"processing mrvn/{game}/{xml_filename}")
            full_xml_filename = os.path.join(in_dir, xml_filename)
            assert xml_filename in ent_filename.keys(), "Unexpected .xml file in mrvn/"
            # NOTE: validate w/ pytest first! not secure against malicious data!
            # TODO:
            # if not unsafe:
            #     xml_ent_schema.validate(full_xml_filename)
            xml_file = minidom.parse(full_xml_filename)
            ...
            # foreach .json: apply overrides
            # credit .json contributor(s) in a comment above definition
            # override header (index by Entity)
            # color
            # box
            # model

            # override keys (index by keyname)
            # type (copy any choiceType that comes up)
            # name
            # default
            # description

            # override Spawnflags (index by bit)
            # name
            # default
            # description

            # override Notes (preserve "Introduced by Source / Titanfall" on first line)
            with open(os.path.join(out_dir, ent_filename[xml_filename]), "w") as ent_file:
                xml_file.writexml(ent_file)
            # TODO: header comments get a little mangled
            # -- might need to clean up post-write?
        # TODO: check for unused choiceTypes
