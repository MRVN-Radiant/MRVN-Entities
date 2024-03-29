# StyleGuide

This is a reference guide for if you want consistency

If you don't mind your code standing out, feel free to ignore

Not gonna be *strongly* enforcing anything, so don't worry about that


## General
 * Colour
   - Default point color is "1 0 1"
   - Default group color is "0 .7 0"
   - Ziplines (`move_rope`) are yellow (like in Apex) ".8 .5 .1"
   - Use Hammer / `base.fgd` colours where possible
 * Documentation
   - Cite your sources (e.g. `scripts/r1_soundscripts.txt`) in a code comment or pull request thread
     > NOTE: `.json` doesn't like comments
 * Debugging
   - MRVN-Radiant will complain about memory leaks, HashedCache & stacktraces on exit, everything up to the error will be parsed
     - NOTE: MRVN-Radiant doesn't tell you where the parsing error happened, I plan to fix this in future
   - Comment out suspect code (temporarily)
   - Look out for `&` (xml escape character [e.g. `&lt;`])
   - Check for any empty fields `name=""`
   - Check for unguarded values `value=1`
   - Use your debug prints, or `import pdb` if you prefer


### Examples
 * Input
   - [`pilot/info_example.json`](https://github.com/MRVN-Radiant/MRVN-Entities/blob/main/pilot/info_example.json)
 * Output
   - [`simulacrum/info_example.ent`](https://github.com/MRVN-Radiant/MRVN-Entities/blob/main/simulacrum/info_example.ent)

## Trigger Colours

[`io_import_rbsp`](https://github.com/snake-biscuits/io_import_rbsp) brush entity colours:

```python
purple = (0.527, 0.006, 1.000)
orange = (0.947, 0.202, 0.004)
mauve = (1.000, 0.026, 0.290)
red = (1.000, 0.007, 0.041)
teal = (0.017, 1.000, 0.246)
lime = (0.224, 1.000, 0.000)
pink = (0.947, 0.010, 0.549)
blue = (0.028, 0.584, 0.947)

palette = {  # classnames
           "envmap_volume": purple,
           "light_probe_volume": purple,
           "light_environment_volume": purple,
           "trigger_capture_point": orange,
           "trigger_hurt": red,
           "trigger_indoor_area": purple,
           "trigger_multiple": orange,
           "trigger_once": orange,
           "trigger_out_of_bounds": mauve,
           "trigger_soundscape": purple,
           # editorclasses
           "trigger_checkpoint": teal,
           "trigger_checkpoint_forced": teal,
           "trigger_checkpoint_safe": teal,
           "trigger_checkpoint_silent": teal,
           "trigger_checkpoint_to_safe_spots": teal,
           "trigger_deadly_fog": red,
           "trigger_death_fall": red,
           "trigger_flag_clear": lime,
           "trigger_flag_set": lime,
           "trigger_flag_touching": lime,
           "trigger_friendly": pink,
           "trigger_friendly_follow": pink,
           "trigger_fw_territory": blue,
           "trigger_level_transition": teal,
           "trigger_mp_spawn_zone": blue,
           "trigger_no_grapple": mauve,
           "trigger_quickdeath": red,
           "trigger_quickdeath_checkpoint": red,
           "trigger_spawn": blue,
           "trigger_teleporter": blue}
```

TL;DR:
 - `ambient/environment` = purple
 - `general/trigger` = orange
 - `general/out_of_bounds` = mauve
 - `singleplayer/checkpoints` = teal
 - `singleplayer/flags` = lime (scripts)
 - `trigger_friendly` = pink
 - `singleplayer/level_change` = teal
 - `hazards` = red
 - `misc` = blue (spawn zones etc.)


## Python

Don't upset `flake8` & try to follow [The Zen of Python](https://peps.python.org/pep-0020/)


## JSON

> TODO: recommend a `.json` linter

Order:
 * Try to maintain order of `index` 1st, `override` 2nd
 * Order of Appearance
   - ent header
     `<point name="info_example">`
     > name (index)
     > type (override)
     > box: bounds (must enclose `0 0 0`)
     > color: RGB floats
     > model: filename
       * should add a TODO for creating a `.obj` editor model
   - ent description
   - keys
     `<keytype key="keyname" name="name" value="default">description</keytype>`
     > keyname (index)
     > keytype (overrides, comes second)
     > name
     > default
     > description
   - spawnflags
   - notes
 * `.json` can reorder keys
 * Order should reflect how often the key is used
   - `targetname` at the top
   - try to group keys with shared purpose
   - Use Source key orders for reference: [VDC](https://developer.valvesoftware.com/wiki/List_of_Team_Fortress_2_Entities)


## XML

* Use an XML linter
   - xmllint (provided by libxml2-utils) for Vim
   - XML Tools (Plugins > Plugin Admin > Search & Install) for Notepad++
 * MRVN will get memory leaks if XML has any errors
   - avoid special characters like &, < and >
     > use &amp;, &lt; and &gt; instead
   - make sure tags are formatted correctly
     > quoted values
     > spaces between options
     > some empty tags are OK
 * Look at "entities.ent" in "ApexLegends.game/ApexLegends/" for quake3 defs
   - Haven't found tag types listed anywhere else (yet.)
 * Check out https://developer.valvesoftware.com/wiki/Base.fgd/Portal_2
   - Lots of functionality is cut
     > No Inputs or Outputs
     > No vscripts list in entity


### `@PointClass` `.fgd` entities -> `.xml`

```xml
<point name="entity_name" color="1 0 1" box="-8 -8 -8 8 8 8">
Brief description
-------- KEYS --------
<boolean key="example" name="Helpful name" value="0">Helpful description (default=false)</boolean>
-------- SPAWNFLAGS --------
<flag key="FIRST" name="First" bit="0">Brief description (if needed)</flag>
<flag key="SECOND" name="Second" bit="1"></flag>
<!-- fgd files seem to start counting bits from 1, rather than 0 -->
-------- NOTES --------
Inherited from Source
Titanfall adds ...
</>
```


### `@SolidClass` `.fgd` entities -> `.xml`
```xml
<group name="entity_name" color="0 .7 0">
Brief description
-------- KEYS --------
<boolean key="example" name="Helpful name" value="0">Helpful description (default=false)</boolean>
-------- SPAWNFLAGS --------
<flag key="FIRST" name="First" bit="0">Brief description (if needed)</flag>
<flag key="SECOND" name="Second" bit="1"></flag>
<!-- fgd files seem to start counting bits from 1, rather than 0 -->
-------- NOTES --------
New in Titanfall
</group>
```
