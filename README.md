# MRVN-entities
Turns Pilots into Simulacra with the power of fanfiction  
[MRVN-radiant](github.com/MRVN-radiant/MRVN-radiant) entity definition generator

## Dependants:
 * [pySourceSDK/ValveFGD](https://github.com/pySourceSDK/ValveFGD)
 * [snake-biscuits/bsp_tool](https://github.com/snake-biscuits/bsp_tool)
   - [snake-biscuits/bsp_tool_examples](https://github.com/snake-biscuits/bsp_tool_examples)
     - `fgd2ent.py` does the `mrvn/` work, should provide some interactive tools


## Repo Installation

Clone this repo:  

```
$ git clone https://github.com/snake-biscuits/MRVN-entities.git
```  

### Windows

Install dependencies with `pip`  

```
$ py -3.9 -m venv venv
$ call venv/scripts/activate
$ python -m pip --upgrade pip
$ python -m pip install -r requirements.txt
```

### Linux

```
$ python3 -m venv venv
$ source venv/bin/activate
$ python -m pip --upgrade pip
$ python -m pip install -r requirements.txt
```


## MRVN Extension

> TODO: this doesn't work yet
> TODO: look at connecting directly to MRVN-radiant w/ GitHub Actions

 * Copy `simulacrum/` artifact from GitHub Actions
 * Copy `.ent` files into `MRVN-radiant` install
   - `r1o/*.ent` goes in `MRVN-radiant/gamepacks/TitanfallOnline.game/TitanfallOnline/*.ent`
   - `r2/*.ent` goes in `MRVN-radiant/gamepacks/Titanfall2.game/Titanfall2/*.ent`
   - `r5/*.ent` goes in `MRVN-radiant/gamepacks/ApexLegends.game/ApexLegends/*.ent`


## Offline Workflow
 * `bloodhound.py` searches `.fgd` & `.bsp` sources to generate initial `.xml` entities
   - outputs `.xml` to `mrvn/` game subfolder (`r1o`, `r2` or `r5`)
 * **PILOT_NAME_MISSING** writes changes (you write ~~fanfiction~~ documentation)
   - outputs `.json` to `pilot/` game subfolder (`r1o`, `r2` or `r5`)
 * `fuse.py` fuses the contents of `human/` with the generated `.xml`
   - outputs `.ent` to `simulacrum/` game subfolder (`r1o`, `r2` or `r5`)

TL;DR: Bloodhound hunts and Fuse does the dishes

> **NOTE: `simulacrum` will only appear in your working folder**
> -- GitHub Workflows should generate a copy as an artifact


## GitHub Workflow
 - Use local pre-generated `mrvn/` folder
   * You can't just download Apex Legends as a GitHub Action
   * Generate `mrvn/` on your own PC & push to GitHub **(only if you need to!)**
 - write `.json` updates to entity definition(s) in `pilot/`
 - push
 - wait for GitHub Actions to run
 - collect latest `simulacrum/` artifact


## TODOs
 * Write `fuse.py`
   - parse `.xml`
   - parse `.json`
   - apply changes
   - write to `simulacrum/<game>/<block_entities>.ent`
 * Write `quality_assurance.py`
   - verify `.json` has good data, no typos
   - don't enforce styleguide, essentials only
   - break if:
     * `contributors` missing
     * invalid index for `block`, `entity`, `key` or `spawnflag`
   - suggest fixes
 * GitHub Workflows
   - lint `.xml`
   - run `quality_assurance.py`
   - run `fuse.py`
   - turn `simulacrum/` into an artifact
 * Documentation
   - using `fgd2ent.py` to compare `omega_entity` to `fgd.entities` to find the "Ur" entity
