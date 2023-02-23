"""quick & dirty wrapper to retarget infiles & outfiles of bsp_tool_examples/fgd2ent.py"""
import collections
import fnmatch
import functools
import os
import re
from typing import Any, Dict, List, Set, Union

import bsp_tool
import valvefgd


MapDict = Dict[str, bsp_tool.base.Bsp]
Entity = Dict[str, str]
# ^ {"key": "value"}
OmegaEntity = Dict[str, List[str]]
# ^ {"key": ["value1", "value2"]}


def ur_ent(maps: MapDict, classname: str = None, **filters: Entity) -> OmegaEntity:
    """Find 'ur' entity (all keys & values used in official maps)"""
    # NOTE: will get a handful of false positives from renamed ents w/ forgotten key values
    if classname is not None:  # add classname to filters
        filters["classname"] = classname
    assert "classname" in filters
    out = collections.defaultdict(set)
    for map_name in maps:
        bsp = maps[map_name]
        for ent in sum(bsp.search_all_entities(**filters).values(), start=list()):
            for key, value in ent.items():
                out[key].add(value)
    return {k: sorted(out[k]) for k in sorted(out)}


Dossier = Dict[str, Union[str, OmegaEntity]]

class_types = dict(PointClass="point", KeyFrameClass="point", MoveClass="point",
                   NPCClass="point", SolidClass="group")


def id_ent(omega_entity: OmegaEntity, fgd: valvefgd.Fgd) -> Dossier:
    # TODO: force fgd baseclass (default: omega_entity["classname"])

    # editorclass -> classname override
    og_classname, og_editorclass = omega_entity["classname"], omega_entity.get("editorclass")
    omega_entity["classname"] = og_editorclass if og_editorclass is not None else og_classname
    if "editorclass" in omega_entity:
        omega_entity.pop("editorclass")
    # NOTE: MRVN-radiant remap will reverse this, grouping by editorclass just make writing easier
    classname = omega_entity["classname"][0]  # new classname, overridden by editorclass if present

    omega_keys = set(omega_entity.keys())
    out = {"classname": classname,
           "ur": omega_entity,
           "type": "point",
           "new": omega_keys,
           "shared": set(),
           "old": set(),
           "spec": None}
    # NOTE: og_classname is the fgd entity classname we want; editorclasses wouldn't appear in fgds afaik
    if og_classname not in [e.name for e in fgd.entities]:
        out["origin"] = "Titanfall"
        if any([v.startswith("*") for v in omega_entity.get("model", list())]):  # brush entity
            out["new"].remove("model")
            out["type"] = "group"
        if any([k.startswith("*coll") or k.startswith("*trigger") for k in omega_entity.keys()]):
            out["type"] = "group"
            # NOTE: xml_ent will remove these keys for us
        if "origin" in out["new"]:  # automatically added by Radiant
            out["new"].remove("origin")
        return out
    # fgd baseclass found
    fgd_entity = fgd.entity_by_name(og_classname)  # ignore editorclass
    fgd_keys = {p.name for p in fgd_entity.properties}
    out.update({"origin": "Source",
                "type": class_types[fgd_entity.class_type],
                "new": omega_keys.difference({*fgd_keys, "origin"}),
                "shared": omega_keys.intersection({*fgd_keys, "origin"}),
                "old": fgd_keys.difference({*omega_keys, "origin"}),
                "spec": fgd_entity})
    return out


# .ent (XML) assemblers
def camelCase(snake_case: str) -> str:
    """choice type name formatter"""
    out = list()
    for word in snake_case.split("_"):
        out.append(word[0].upper() + word[1:])
    out = "".join(out)
    return out[0].lower() + out[1:]


def xml_choices(choice_property: valvefgd.FgdEntityProperty) -> (str, str):
    type_name = camelCase(choice_property.name)
    out = [f'<list name="{type_name}">']
    for choice in choice_property.choices:
        out.append(f'  <item name="{choice.display_name}" value="{choice.value}"/>')
    out.append("</list>\n")
    return type_name, "\n".join(out)


log2 = {2 ** i: i for i in range(32)}  # for spawnflags conversion


def xml_spawnflags(spawnflags: List[valvefgd.FgdEntitySpawnflag]) -> str:
    out = list()
    for flag in spawnflags:
        # flag.display_name, value, default_value
        name = "_".join(["FLAG", *map(str.upper, flag.display_name.split())])
        # TODO: check for separators in name that could be descs (",.-" etc.)
        bit = log2[flag.value]
        default = int(flag.default_value)
        out.append(f'<flag key="{name}" name="{name}" bit="{bit}" value="{default}">TODO: description</flag>')
    return out


def ent_definitions(ent_spec: valvefgd.FgdEntity) -> Dict[str, Dict[str, Any]]:
    out = dict()
    ancestors = list(ent_spec.parents)
    for ancestor in ancestors:
        ancestors.extend(ancestor.parents)  # keep digging
        for defs in getattr(ancestor, "defintions", list()):
            for d in defs:
                if d["name"] not in out:  # newest overrides
                    out[d["name"]] = d["args"]
    return out


key_types = {"float": "real", "boolean": "boolean", "integer": "integer", "studio": "model",
             "sound": "sound", "target_source": "targetname", "target_dest": "targetname",
             "angle": "angles"}
# ^ {"fgd_key": "key_type"}


def guess_key_type(key_name: str, key_values: Set[str]) -> str:
    """ur_key key_type"""
    # https://github.com/MRVN-Radiant/MRVN-Radiant/blob/main/radiant/eclass_xml.cpp#L49-L68
    # TODO: better checks for false positives
    key_values.discard("")
    is_vec3, is_vec4, is_path = False, False, False
    if key_name.lower() == "scale":
        return "real"
    # TODO: regex numbers
    if all(map(lambda v: v.count(" ") == 3, key_values)):
        is_vec3 = True
    if all(map(lambda v: v.count(" ") == 4, key_values)):
        is_vec4 = True
    if any(map(lambda v: "/" in v.replace("\\", "/"), key_values)):
        is_path = True
    if "color" in key_name.lower() and is_vec3 and not is_vec4:
        return "color"
    if "model" in key_name.lower() and is_path:
        return "model"
    # if is_path:
    # -- sound (need radiant to index soundscripts like source)
    # -- texture (sprites, light texture)
    # -- ui & script are possibilities, but aren't supported by Radiant (yet.)
    if "target" in key_name.lower():
        return "targetname"
    if "angles" in key_name.lower() and is_vec3:
        return "angles"
    return "string"


def sanitise_desc(desc: str) -> str:
    out = desc
    subs = {". ": ".\n", "&": "&amp;", "<": "&lt;", ">": "&gt;"}
    for old, new in subs.items():
        out = out.replace(old, new)
    return out


common_keys = {"targetname": ("Name", "The name that other entities refer to this entity by."),
               "model": ("World Model", ""),
               "angles": ("Pitch Yaw Roll (Y Z X)", "This entity's orientation in the world.\n"
                          "Pitch is rotation around the Y axis, Yaw is the rotation around the Z axis, Roll is the rotation around the X axis.")}  # noqa
# ^ similar to guess_key_type, but for descriptions


def xml_ent(dossier: Dossier) -> (str, Set[str]):  # ("<point name="entity">...</point>", {'<list name="choiceType"'})
    """generate xml representation of entity from dossier"""
    out = list()  # lines of xml text
    choice_types = set()  # blocks of xml choiceType definitions
    defs = ent_definitions(dossier["spec"]) if dossier["spec"] is not None else dict()
    head = f'<{dossier["type"]} name=\"{dossier["classname"]}\"'
    color = " ".join(map(str, defs.get("color", [1, 0, 1])))
    bonus = list()
    if "studio" in defs:  # editor model
        studio = defs["studio"][0]
        out.append(f'<!-- TODO: convert {studio} to .obj -->')
        bonus.append(f'model="{studio}"')
    elif dossier["type"] == "point":
        bonus.append('box="-8 -8 -8 8 8 8"')
    out.append(" ".join([head, f'color="{color}"', *bonus]) + ">")
    if dossier["spec"] is not None:  # source based
        out.append(sanitise_desc(dossier["spec"].description))
        fgd_keys = [p for p in dossier["spec"].properties if p.name not in dossier["old"]]
        spawnflags = dossier["spec"].spawnflags
    else:  # dummy spec
        fgd_keys = list()
        spawnflags = list()
    # keys
    out.append("----- KEYS -----")
    # fgd keys (sourced from fgd and present in ur_entity)
    for key in fgd_keys:  # preserve fgd order
        if key.value_type == "choices":
            # choices_dict = {c.display_name.lower(): c.value for c in key.choices}
            if {c.display_name.lower(): c.value for c in key.choices} == {"no": 0, "yes": 1}:
                key_type = "boolean"  # ridiculous edge case
            else:
                key_type, choice_list = xml_choices(key)
                choice_types.add(choice_list)
        else:
            key_type = key_types.get(key.value_type, "string")
        key_description = "" if key.description is None else key.description
        key_description = sanitise_desc(key_description)
        out.append(" ".join([f'<{key_type} key="{key.name}" name="{key.display_name}"',
                             f'value="{key.default_value}">{key_description}</{key_type}>']))
    # xml keys (sourced from ur_entity)
    omega_keys = {k for k in dossier["new"] if k not in ("classname", "spawnclass")}
    for key_name in sorted(omega_keys):  # alphabetical order
        # NOTE: will get a handful of false positives from renamed ents w/ forgotten key values
        if key_name.startswith("*coll") or key_name.startswith("*trigger"):
            continue  # skip omega entity collision / brushes
        elif key_name != "spawnflags":  # general keys
            key_type = guess_key_type(key_name, dossier["ur"][key_name])
            key_display_name, key_desc = common_keys.get(key_name, (key_name, "New in Titanfall; TODO: identify"))
            out.append(f'<{key_type} key="{key_name}" name="{key_display_name}">{key_desc}</{key_type}>')
        else:  # identify new spawnflags
            omega_spawnflag = functools.reduce(lambda a, b: a | b, map(int, dossier["ur"]["spawnflags"]))
            used_flags = f"{omega_spawnflag:032b}"  # bits
            spawnflags = [valvefgd.FgdEntitySpawnflag(display_name=f"UNKNOWN_{i}", value=2**i, default_value=0)
                          for i in range(32) if used_flags[::-1][i] == "1"]  # sure hope this lines up
    # spawnflags
    if len(spawnflags) > 0:
        out.append("----- SPAWNFLAGS -----")
        out.extend(xml_spawnflags(spawnflags))
    # notes
    out.append("----- NOTES -----")
    out.append(f"Introduced by {dossier['origin']}")
    if dossier["origin"] == "Source":
        if len(omega_keys) > 0:
            out.append(f"Added: {', '.join(sorted(omega_keys))}")
        old_keys = {*dossier["old"]}
        if len(old_keys) > 0:
            out.append(f"Removed: {', '.join(sorted(old_keys))}")
        if len(omega_keys) != 0 or len(old_keys) != 0:
            out.append("TODO: identify changes")
    # TODO: find a ratio at which you can safely say: "total refactor"
    out.append(f'</{dossier["type"]}>')
    return "\n".join(out), choice_types


def batch(maps: MapDict, fgd: valvefgd.Fgd, classnames: List[Union[str, Dict]]) -> (Dict[str, Set[str]], List[str]):
    """Re-use choice types"""
    choice_types = collections.defaultdict(set)
    # ^ {'<list name="choice_type">...': {"classname", ...}}
    ents = list()
    for x in classnames:
        if isinstance(x, str):
            filters = dict(classname=x)
        elif isinstance(x, dict):
            filters = x
        ent_omega = ur_ent(maps, **filters)

        # TODO: feed base classname to id_ent (base classes in general would be handy)
        ent_dossier = id_ent(ent_omega, fgd)
        ent_txt, ent_choices = xml_ent(ent_dossier)
        # TODO: ent_as_def(ent_dossier) for TrenchBroom
        # TODO: ent_as_fgd(ent_dossier) for Hammer/Hammer++
        ents.append(ent_txt)
        for ct in ent_choices:
            choice_types[ct].add(filters["classname"])
        # TODO: ensure list name of each ent_choice_list is unique
        # -- camelCase w/ entity_name
        # -- probably need to regex first line
    ents = sorted(ents, key=lambda x: re.match(r'<.* name="([^"]+)".*', x).groups()[0])
    return choice_types, ents


if __name__ == "__main__":
    header = """<?xml version="1.0"?>
<!--
    Titanfall 2 entity definitions for MRVN-radiant
        Generated by MRVN-entities
        Spawnpoint, hardpoint, ctf flag & zipline definitions by catornot (2022-11-2)
        Bounding Boxes and Models by snake-biscuits (2022-11-6)
-->
<!-- TODO:
    Identify broken / unused / unimplemented keys
    Test if Titanfall can handle missing entity keys (some scripts might complain)
-->
<classes>
<!--
=============================================================================
 OPTION KEY TYPES
=============================================================================
-->\n"""

    footer = """</classes>"""

    maps = dict()
    # TODO: allow recursion to load every Apex Legends Season at once
    outdir = input("INPUT: sub-folder of generated for output (e.g. r1): ")
    os.makedirs(f"mrvn/{outdir}", exist_ok=True)
    md_count = int(input("INPUT: number of map directories: "))
    for i in range(md_count):
        md = input(f"INPUT: map directory #{i}: ")
        print("Searching...")
        im = {os.path.join(md, m): None for m in fnmatch.filter(os.listdir(md), "*.bsp")}
        print(f"Found {len(im)} maps")
        maps.update(im)
    del im  # reduce memory costs?
    fgd_path = input("INPUT: .fgd file to search for definitions: ")
    print("Loading fgd...")
    fgd = valvefgd.FgdParse(fgd_path)
    print("Loaded!")

    print(f"Loading all {len(maps)} maps...")
    maps = {m: bsp_tool.load_bsp(m) for m in maps}
    print(len(maps), "Loaded!")

    # all Titanfall Entity Lumps
    ent_blocks = ("ENTITIES", *(f"ENTITIES_{x}" for x in ("env", "fx", "script", "spawn", "snd")))

    print("Gathering entity classnames...")
    all_classnames = collections.defaultdict(set)
    for bsp in maps.values():
        for block in ent_blocks:
            for entity in getattr(bsp, block):
                all_classnames[block].add((entity["classname"], entity.get("editorclass", "")))
                # NOTE: default "" editorclass means raw info_target & it's editorclasses should be split

    for block in ent_blocks:
        print(len(all_classnames[block]), "classnames found in", block)

    for block in ent_blocks:
        print(f"Batching {block}...")
        ent_filters = [dict(zip(("classname", "editorclass"), t)) for t in all_classnames[block]]
        choice_types, ents = batch(maps, fgd, ent_filters)
        print(f"Writing {outdir}/{block}.xml...")
        with open(f"mrvn/{outdir}/{block}.xml", "w") as ent_file:
            ent_file.write(header + "\n")
            ent_file.write("\n\n".join([f"<!-- used by {', '.join(v)} -->\n{k}"
                                        for k, v in sorted(choice_types.items(), key=lambda a: a[0])]))
            ent_file.write("""\n<!--
=============================================================================
 ENTITIES IN ALPHABETICAL ORDER
=============================================================================
-->\n""")
            ent_file.write("\n\n".join(ents))
            ent_file.write("\n</classes>\n")
        print("Done!")
    print("Finished!")
