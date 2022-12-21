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

key_types = {"real": float, "integer": int, "string": str, "boolean": bool,
             "angles": str, "model": str, "color": str,  # TODO: regex
             "targetname": str}  # TODO: see if I forgot any
# NOTE: origin & any *keys (added by compiler) should not appear in definitions
# -- we might override origin in future actually... some ents might need deeper descriptions
key_type_defaults = {"float": "1.0", "integer": "0", "string": "", "boolean": "0",
                     "angles": "0 0 0", "model": "", "color": "1 0 1", "targetname": ""}
# NOTE: choiceTypes should default to first Option
# -- any type not in key_types should be considered a choiceType


def override_header(xml_ent: minidom.Element, json_ent: dict, attr: str, default=None):
    value = xml_ent.getAttribute(attr.lower())  # Color -> color
    if value == "":
        value = default
    value = json_ent.get(attr, value)
    if value is not None:
        xml_ent.setAttribute(attr.lower(), value)


def override_key(xml_key: minidom.Element, json_key: dict):
    xml_key.tagName = json_key.get("type", xml_key.tagName)
    for attr in ("name", "value"):
        xml_key.setAttribute(attr, json_key.get(attr, xml_key.getAttribute(attr)))
        # NOTE: will be set to "" if not present in xml_key
    xml_desc = xml_key.childNodes[0].data  # assuming this is always present in mrvn/*.xml
    xml_key.childNodes = [minidom.Text()]
    xml_key.childNodes[0].replaceWholeText(json_key.get("description", xml_desc))


# TODO: new_key, override_spawnflag & new_spawnflag functions


if __name__ == "__main__":
    # TODO: make failstates more explicit and give useful error messages
    # -- ideally gather all errors & report changes needed to input
    for game in filter(lambda p: os.path.isdir(os.path.join("mrvn", p)), os.listdir("mrvn")):
        print(f"processing mrvn/{game}/")
        in_dir = os.path.join("mrvn", game)
        out_dir = os.path.join("simulacrum", game)
        os.makedirs(out_dir, exist_ok=True)

        print(f"gathering overrides from pilot/{game}/")
        json_dir = os.path.join("pilot", game)
        assert os.path.exists(json_dir)

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

        # utility node
        newline = minidom.Text()  # Can't initialise w/ a value?
        newline.replaceWholeText("\n")

        for xml_filename in fnmatch.filter(os.listdir(in_dir), "*.xml"):
            print(f"processing mrvn/{game}/{xml_filename}")
            full_xml_filename = os.path.join(in_dir, xml_filename)
            assert xml_filename in ent_filename.keys(), "Unexpected .xml file in mrvn/"
            # NOTE: validate w/ pytest first! not secure against malicious data!
            # TODO:
            # if not unsafe:
            #     xml_ent_schema.validate(full_xml_filename)
            xml_file = minidom.parse(full_xml_filename)
            classes_node = xml_file.getElementsByTagName("classes")[0]
            elements = tuple(filter(lambda x: isinstance(x, minidom.Element), classes_node.childNodes))
            # choiceTypes = {e.attributes["name"].value: e for e in elements if e.tagName == "list"}
            # ^ choiceTypes present in mrvn .xml
            choiceTypes = set()  # choiceTypes to add
            entities = {e.attributes["name"].value: e for e in elements if e.tagName in ("point", "group")}
            for json_filename in ent_overrides[xml_filename]:
                with open(os.path.join(json_dir, json_filename)) as json_file:
                    json_ent = json.load(json_file)
                # index entity
                if json_ent["Entity"] not in entities:  # editorclass?
                    # see https://github.com/MRVN-Radiant/MRVN-Radiant/issues/26
                    print("Couldn't find", json_ent["Entity"], "to override (editorclass?). Skipping...")
                    continue
                xml_ent = entities[json_ent["Entity"]]
                # credit contributors
                contributors_comment = minidom.Comment(", ".join(json_ent["Contributors"]))
                classes_node.childNodes.insert(classes_node.childNodes.index(xml_ent), contributors_comment)
                classes_node.childNodes.insert(classes_node.childNodes.index(xml_ent), newline)
                # override entity head node attributes
                override_header(xml_ent, json_ent, "Color", default="1 0 1")
                if xml_ent.tagName == "point":
                    override_header(xml_ent, json_ent, "Box", default="-8 -8 -8 8 8 8")
                override_header(xml_ent, json_ent, "Model")
                # override entity keys
                xml_keys = {k.attributes["key"].value: k for k in xml_ent.childNodes
                            if k.attributes is not None and "key" in k.attributes}
                json_keys = {k["keyname"]: k for k in json_ent.get("Keys", dict())}
                choiceTypes.update({t for t in {k.get("type", "string") for k in json_keys.values()} if t not in key_types})
                for keyname in set(xml_keys).intersection(set(json_keys)):
                    override_key(xml_keys[keyname], json_keys[keyname])
                # write new keys
                key_ends = [" ".join(["-" * 5, x, "-" * 5]) for x in ("SPAWNFLAGS", "NOTES")]
                # TODO: find a better way to insert keys in the right place
                # TODO: sort keys?
                last_key_index = min([i for i, e in enumerate(xml_ent.childNodes)
                                      if isinstance(e, minidom.Text) and any([t in e.data for t in key_ends])])
                for keyname in set(json_keys).difference(set(xml_keys)):  # new keys
                    json_key = json_keys[keyname]
                    new_key = xml_file.createElement(json_key["type"])
                    new_key.setAttribute("keyname", keyname)
                    new_key.setAttribute("name", json_key.get("name", keyname))
                    new_key.setAttribute("value", json_key.get("value", ""))  # default
                    new_key.childNodes = [minidom.Text()]
                    new_key.childNodes[0].replaceWholeText(json_key.get("description", ""))
                    xml_ent.childNodes.insert(last_key_index, new_key)
                    last_key_index += 1
                ...
                # TODO: override SpawnFlags
                # -- add ----- SPAWNFLAGS ----- line if absent
                # -- name
                # -- default
                # -- description
                # TODO: override Notes (preserve "Introduced by Source / Titanfall" on first line)
            # TODO: add choiceTypes
            # write changes
            with open(os.path.join(out_dir, ent_filename[xml_filename]), "w") as ent_file:
                xml_file.writexml(ent_file)
            # TODO: header comments get a little mangled
            # -- might need to clean up post-write?
        # TODO: check for unused choiceTypes
