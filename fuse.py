import collections
import fnmatch
import html
import json
import os
import sys
from xml.etree import ElementTree

# parsing xml & json can be very unsafe with a lazy parser, always verify schema before diving in!
if not sys.argv != (sys.argv[0], "--unsafe"):
    unsafe = False
    # from tests import test_json, test_xml
else:
    unsafe = True
    # TODO: UserWarning


ent_filename = {"ENTITIES.xml":        "entities.ent",
                "ENTITIES_env.xml":    "environment_entities.ent",
                "ENTITIES_fx.xml":     "effects_entities.ent",
                "ENTITIES_script.xml": "script_entities.ent",
                "ENTITIES_spawn.xml":  "spawn_entities.ent",
                "ENTITIES_snd.xml":    "sound_entities.ent"}

key_types = {"string": str, "array": str, "integer": int, "boolean": bool, "real": float,
             "angle": float, "direction": str, "real3": str, "angles": str, "color": str,  # float x3
             "target": str, "targetname": str,  # identifiers
             "sound": str, "texture": str, "model": str, "skin": str}  # paths

key_type_defaults = {"string": "", "array": "", "integer": "0", "boolean": "0", "real": "1",
                     "angle": "0", "direction": "0 1 0", "real3": "0 0 0", "angles": "0 0 0", "color": "1 0 1",
                     "target": "", "targetname": "",
                     "sound": "", "texture": "", "model": "", "skin": ""}
# NOTE: tests.test_json will use regex to ensure values conform to key_type (doesn't yet)

# TODO: choiceTypes should default to first list item
# -- any type not in key_types should be considered a choiceType
# -- throw a Warning if choiceType is not defined and default to string


def update_ent_metadata(xml_ent: ElementTree.Element, json_spec: dict, attr: str, default=None):
    """Sets one attribute at a time; handles type conversions & default heirarchy"""
    value = xml_ent.get(attr.lower())  # Color -> color
    if value is None:
        value = default
    value = json_spec.get(attr, value)
    if value is not None:
        xml_ent.set(attr.lower(), value)


def new_key(json_spec: dict) -> ElementTree.Element:
    """Not the same as: e = Element('x'); update_key(e, json_spec)"""
    out = ElementTree.Element(json_spec["type"])
    out.set("key", json_spec["keyname"])  # compiled name
    out.set("name", json_spec.get("name", json_spec["keyname"]))  # editor friendly name
    # TODO: key_type_defaults?, choiceType defaults need a Dict[str, choiceType_spec] arg
    out.set("value", json_spec.get("value", ""))  # default value
    out.text = html.escape(json_spec.get("description", ""))  # use / effects
    return out


def update_key(xml_key: ElementTree.Element, json_spec: dict):
    xml_key.tag = json_spec.get("type", xml_key.tag)
    for attr in ("name", "keyname", "default", "value"):
        if json_spec.get(attr) is None and xml_key.get(attr) is None:
            continue
        xml_key.set(attr, json_spec.get(attr, xml_key.get(attr)))
    # TODO: UX DESIGN QUESTION: do we expect pilot/*.json to html.escape() descriptions?
    xml_key.text = json_spec.get("description", xml_key.text)


def new_spawnflag(json_spec: dict) -> ElementTree.Element:
    out = ElementTree.Element("flag")
    out.set("key", json_spec["name"])
    out.set("name", json_spec["name"])
    out.set("bit", json_spec["bit"])  # bit set / unset by flag
    default = {"False": "0", "True": "1"}[json_spec.get("default", "False")]
    out.set("value", str(default))
    out.text = html.escape(json_spec.get("description", ""))  # use / effects
    return out


def update_spawnflag(xml_flag: ElementTree.Element, json_spec: dict):
    keyname = json_spec.get("name", xml_flag.get("key"))
    xml_flag.set("key", keyname)
    xml_flag.set("name", keyname)
    xml_flag.set("value", json_spec.get("value", xml_flag.get("value")))
    # TODO: UX DESIGN QUESTION: do we expect pilot/*.json to html.escape() descriptions?
    xml_flag.text = json_spec.get("description", xml_flag.text)


def new_choice_type(json_spec: dict) -> ElementTree.Element:
    out = ElementTree.Element("list")
    out.set("name", json_spec["Name"])
    for name, value in json_spec["Options"].items():
        option = ElementTree.Element("item")
        option.set("name", name)
        option.set("value", value)
        out.append(option)
    return out


if __name__ == "__main__":
    # TODO: make failstates more explicit and give useful error messages
    # -- ideally gather all errors & recommend changes to pilot/*.json (mrvn/*.xml should be stable)
    # NOTE: we use .__getitem__ rather than .get in cases where missing keys should fail
    # -- this doesn't tell a casual user what they forgot to add; we need to rectify that.
    # TODO: pre-process input files w/ schema before running fuse; leave input validation up to tests
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
            full_json_filepath = os.path.join(json_dir, json_filename)
            # if not unsafe:
            #     test_json.test_entity(full_json_filepath)
            try:
                with open(full_json_filepath) as json_file:
                    entity = json.load(json_file)
            except Exception as exc:
                print(f"{json_filename} broke: {exc.__name__}({exc.msg})")  # TODO: more detail / helpful suggestions
            ent_overrides[f"{entity['Block']}.xml"].add(json_filename)
        print(f"collected {sum(map(len, ent_overrides.values()))} entities across {len(ent_overrides)} blocks")

        print(f"gathering choiceTypes from pilot/{game}/choiceTypes")
        choice_type_dir = os.path.join(json_dir, "choiceTypes")
        assert os.path.exists(choice_type_dir)
        cached_choice_types = dict()
        # ^ {"choiceType": {"Name": "choiceType", "Options": dict(...)}}
        for json_filename in fnmatch.filter(os.listdir(choice_type_dir), "*.json"):
            full_json_filepath = os.path.join(choice_type_dir, json_filename)
            # if not unsafe:
            #     tests.test_json.test_choiceType(choice_type)
            try:
                with open(full_json_filepath) as json_file:
                    choice_type = json.load(json_file)
            except Exception as exc:
                print(f"{json_filename} broke: {exc.__name__}({exc.msg})")  # TODO: more detail / helpful suggestions
            cached_choice_types.update({json_filename[:-5]: choice_type})
        print(f"collected {len(cached_choice_types)} choiceType definitions")

        for xml_filename in fnmatch.filter(os.listdir(in_dir), "*.xml"):
            print(f"processing mrvn/{game}/{xml_filename}")
            full_xml_filename = os.path.join(in_dir, xml_filename)
            assert xml_filename in ent_filename.keys(), "Unexpected .xml file in mrvn/"
            xml_file = ElementTree.parse(full_xml_filename)
            used_choice_types = set()
            ent_classes_node = xml_file.getroot()
            entities = {e.get("name"): e for e in ent_classes_node if e.tag in ("point", "group")}
            for json_filename in ent_overrides[xml_filename]:
                with open(os.path.join(json_dir, json_filename)) as json_file:
                    json_ent = json.load(json_file)
                # index entity
                ent_name = json_ent["Entity"]
                if ent_name in entities:
                    xml_ent = entities[ent_name]
                else:  # new ent
                    try:
                        assert "Type" in json_ent, "'Type' must be defined"
                        ent_type = json_ent["Type"]
                        assert ent_type in ("point", "group"), "'Type' must be either 'point' or 'group'"
                        print(f"adding new entity: {ent_name}")
                        ent_index = sorted([*entities.keys(), ent_name]).index(ent_name)
                        ent_classes_node.insert(ent_index, ElementTree.Element(json_ent["Type"], name=ent_name))
                        xml_ent = ent_classes_node[ent_index]
                    except AssertionError as ae:
                        print(f"NEW entity: {ent_name} .json is missing data: {ae!s}; Skipping...")
                    except Exception as exc:
                        exception_type = exc.__class__.__name__
                        print(f"Failed to add {ent_name} to {full_xml_filename} ({exception_type}); Skipping...")
                    # NOTE: tests will complain if new ent isn't listed in blocks.json
                # add .json data
                contributors_comment = ElementTree.Comment(", ".join(json_ent["Contributors"]))
                ent_classes_node.insert(ent_classes_node[::].index(xml_ent), contributors_comment)
                update_ent_metadata(xml_ent, json_ent, "Color", default="1 0 1")
                if xml_ent.tag == "point":
                    update_ent_metadata(xml_ent, json_ent, "Box", default="-8 -8 -8 8 8 8")
                update_ent_metadata(xml_ent, json_ent, "Model")
                xml_keys = {k.get("key"): k for k in xml_ent if k.tag != "flag"}
                json_keys = {k["keyname"]: k for k in json_ent.get("Keys", dict())}
                # add new choiceTypes to .ent
                xml_choice_types = {k["type"] for k in xml_keys.values() if k.tag not in key_types}
                json_choice_types = {k["type"] for k in json_keys.values() if k["type"] not in key_types}
                ent_choice_types = xml_choice_types.union(json_choice_types)
                for choice_type in ent_choice_types.difference(used_choice_types):
                    try:
                        ct = new_choice_type(cached_choice_types[choice_type])
                    except KeyError:
                        raise RuntimeError(f"{json_dir}/choiceTypes/{choice_type}.json not found ({json_ent['Entity']})")
                    ent_classes_node.insert(0, ct)
                used_choice_types = used_choice_types.union(ent_choice_types)
                # update xml ent according to json spec
                for keyname in set(xml_keys).intersection(set(json_keys)):
                    update_key(xml_keys[keyname], json_keys[keyname])
                # TODO: cut off the tail & regrow, rather than mutating in place
                last_key_index = len(xml_ent)
                xml_spawnflags = [k for k in xml_ent if k.tag == "flag"]
                if len(xml_spawnflags) > 0:
                    last_key_index = xml_ent[::].index(xml_spawnflags[0]) - 1
                # TODO: ensure "----- SPAWNFLAGS -----" spacer is positioned correctly
                for keyname in set(json_keys).difference(set(xml_keys)):
                    last_key_index += 1
                    xml_ent.insert(last_key_index, new_key(json_keys[keyname]))
                xml_spawnflags = {int(f.get("bit")): f for f in xml_spawnflags}
                json_spawnflags = {int(f.get("bit")): f for f in json_ent.get("SpawnFlags", list())}
                for i in range(32):  # sorting
                    if i not in {*xml_spawnflags, *json_spawnflags}:
                        continue
                ...
                # TODO: override Notes (preserve "Introduced by Source / Titanfall" on first line)
            with open(os.path.join(out_dir, ent_filename[xml_filename]), "wb") as ent_file:
                xml_file.write(ent_file)
        # TODO: check for unused choiceTypes & log warnings
