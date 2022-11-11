raise NotImplementedError("fusey's on smoko mate")

# TODO:
# -- decide on `.json` layout
# --  * write `info_example.json`
# -- for each `ENTITIES.xml`
# --  * parse `.xml`
# --  * collect changes from `.json` (1 per entity, w/ same name)
# --  * credit `.json` contributor(s)
# --  * FUSE `.xml` base with `.json` changes into renamed `.ent`
# --  * write to f"simulacrum/<game>/{ent_filename[xml_filename]}"
# -- mimic pilot regen screen

ent_filename = {"ENTITIES.xml": "entities.ent",
                "ENTITIES_env.xml": "environment_entites.ent",
                "ENTITIES_fx.xml": "effects_entities.ent",
                "ENTITIES_script.xml": "script_entities.ent",
                "ENTITIES_spawn.xml": "spawn_entities.ent",
                "ENTITIES_snd.xml": "sound_entities.ent"}