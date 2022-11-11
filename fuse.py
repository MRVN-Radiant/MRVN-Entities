raise NotImplementedError("fusey's on smoko mate")

# TODO:
# -- decide on `.json` layout
# --  * write `info_example.json`
# -- for each `ENTITIES.xml`
# --  * parse `.xml`
# --  * collect changes from `.json` (1 per entity or choiceType)
# --  * credit `.json` contributor(s) in a comment above definition
# --  * FUSE `.xml` base with `.json` changes into renamed `.ent`
# --  * write to f"simulacrum/<game>/{ent_filename[xml_filename]}"
#
# -- mimic pilot regen screen

ent_filename = {"ENTITIES.xml": "entities.ent",
                "ENTITIES_env.xml": "environment_entites.ent",
                "ENTITIES_fx.xml": "effects_entities.ent",
                "ENTITIES_script.xml": "script_entities.ent",
                "ENTITIES_spawn.xml": "spawn_entities.ent",
                "ENTITIES_snd.xml": "sound_entities.ent"}

types = {"float": "real"}  # fuzzy matching
defaults = {"float": "1.0"}  # allow undefined
# TODO: choiceTypes default to first Option

thesaurus = {"0": ["no", "0", "false"],
             "1": ["yes", "1", "true"]}