# MRVN-Entities
Turns Pilots into Simulacra with the power of fanfiction  
[MRVN-Radiant](github.com/MRVN-radiant/MRVN-radiant) entity definition generator


## Installing `.ent` files in MRVN-Radiant

 * Copy `simulacrum/` artifact from GitHub Actions
 * Copy `.ent` files into `MRVN-Radiant` install
   - `r1o/*.ent` goes in `MRVN-Radiant/gamepacks/TitanfallOnline.game/TitanfallOnline/*.ent`
   - `r2/*.ent` goes in `MRVN-Radiant/gamepacks/Titanfall2.game/Titanfall2/*.ent`
   - `r5/*.ent` goes in `MRVN-Radiant/gamepacks/ApexLegends.game/ApexLegends/*.ent`

MRVN-Radiant will now use the latest entity definitions

<!-- TODO: automate updating `simulacrum/` & adding releases to MRVN-Radiant (pull request) -->


## Dependants
 * [pySourceSDK/ValveFGD](https://github.com/pySourceSDK/ValveFGD)
 * [snake-biscuits/bsp_tool](https://github.com/snake-biscuits/bsp_tool)


## Offline Use

Clone this repo:  

```
$ git clone https://github.com/MRVN-Radiant/MRVN-entities.git
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


## Offline Workflow
 * `bloodhound.py` searches `.fgd` & `.bsp` sources to generate initial `.xml` entities
   - outputs `.xml` to `mrvn/` game subfolder (`r1o`, `r2` or `r5`)
 * **PILOT_NAME_MISSING** writes changes (you write ~~fanfiction~~ documentation)
   - outputs `.json` to `pilot/` game subfolder (`r1o`, `r2` or `r5`)
 * `fuse.py` fuses the contents of `human/` with the generated `.xml`
   - outputs `.ent` to `simulacrum/` game subfolder (`r1o`, `r2` or `r5`)

TL;DR: Bloodhound hunts and Fuse does the dishes


## GitHub / Online Only Workflow
 - Write `.json` updates to entity definition(s) in `pilot/`
 - Push
 - Wait for GitHub Actions to finish
   * Respond to any warnings / errors from your changes
 - Collect latest `simulacrum/` artifact
