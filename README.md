# MRVN-Entities
Turns Pilots into Simulacra with the power of fanfiction  
[MRVN-Radiant](github.com/MRVN-Radiant/MRVN-Radiant) entity definition generator


## Installing `.ent` files in MRVN-Radiant

 * Copy `simulacrum/` artifact from GitHub Actions
 * Copy `.ent` files into `MRVN-Radiant` install
   - `r1o/*.ent` goes in `MRVN-Radiant/gamepacks/TitanfallOnline.game/TitanfallOnline/*.ent`
   - `r2/*.ent` goes in `MRVN-Radiant/gamepacks/Titanfall2.game/Titanfall2/*.ent`
   - `r5/*.ent` goes in `MRVN-Radiant/gamepacks/ApexLegends.game/ApexLegends/*.ent`

MRVN-Radiant will now use the latest entity definitions

<!-- TODO: automate updating `simulacrum/` & adding releases to MRVN-Radiant (pull request) -->


## Dependencies
 * reverse engineering
   - [pySourceSDK/ValveFGD](https://github.com/pySourceSDK/ValveFGD)
   - [snake-biscuits/bsp_tool](https://github.com/snake-biscuits/bsp_tool)
 * processing & validating files
   - `jsonschema`
   - `lxml`
   - `xmlschema`


## Offline Use

Clone this repo:  

```
$ git clone https://github.com/MRVN-Radiant/MRVN-Entities.git
```  

### Windows

Install dependencies with `pip`  

```
$ py -3.13 -m venv .env
$ call .env/scripts/activate
$ python -m pip --upgrade pip
$ python -m pip install -r requirements.txt
```

### Linux

```
$ python3 -m venv .env
$ source .env/bin/activate
$ python -m pip --upgrade pip
$ python -m pip install -r requirements.txt
```


## Offline Workflow
 * `bloodhound.py` searches `.fgd` & `.bsp` sources to generate initial `.xml` entities
   - outputs `.xml` to `mrvn/` game folders (`r1o`, `r2` or `r5`)
 * **PILOT_NAME_MISSING** writes changes (you write ~~fanfiction~~ documentation)
   - outputs `.json` to `pilot/` game folders (`r1o`, `r2` or `r5`)
 * `pytest -vv` checks files against schemas & `blocks.json`
   - validates `mrvn/**/*.xml` & `pilot/**/*.json`
 * `fuse.py` fuses the contents of `pilot/` with `mrvn/`
   - outputs `.ent` to `simulacrum/` game folders (`r1o`, `r2` or `r5`)

TL;DR: Bloodhound hunts and Fuse does the dishes


## GitHub / Online Only Workflow
 - Write `.json` updates to entity definition(s) in `pilot/`
 - Push
 - Wait for GitHub Actions to finish
   * Respond to any warnings / errors from your changes
 - Collect latest `simulacrum/` artifact
