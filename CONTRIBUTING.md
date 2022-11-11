# CONTRIBUTING

fusehound fanfiction goes in `pilot/` subfolders

> TODO: `.json` linter & format checker

See:
 * `STYLE.md` breakdown on entity color palette
   - feel free to define your own category and add it to the list
   - Use the rest as a guide, but don't follow it too closely, it's not a rulebook
 * Examples:
   - input: `mrvn/info_example.xml` (**TODO**)
   - input: [`pilot/info_example.json`](https://github.com/MRVN-radiant/MRVN-entities/blob/maste/pilot/info_example.json)
   - output: [`simulacrum/info_example.xml`](https://github.com/MRVN-radiant/MRVN-entities/blob/maste/simulacrum/info_example.ent)

Order:
 - Try to maintain order of `index` 1st, `override` 2nd
 - Order of Appearance
   * ent header
     `<point name="info_example">`
     - name (index)
     - type (override)
     - box: bounds (must enclose `0 0 0`)
     - color: RGB floats
     - model: filename
       * should add a TODO for creating a `.obj` editor model
   * ent description
   * keys
     `<keytype key="keyname" name="name" value="default">description</keytype>`
     - keyname (index)
     - keytype (overrides, comes second)
     - name
     - default
     - description
   * spawnflags
   * notes
 - `.json` can reorder keys
 - Order should reflect how often the key is used
   * `targetname` at the top
   * try to group keys with shared purpose
   * look at source entity key orders on [VDC](https://developer.valvesoftware.com/wiki/List_of_Team_Fortress_2_Entities)