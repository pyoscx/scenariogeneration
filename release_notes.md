## scenariogeneration release notes

### 2021-05-25 Version 0.3.5
- some documentation updates
- some minor bug fixes
- New Features
    - ParameterReader (similar to catalog reader but for parameterdeclaration of the scenario)
    - Easy creation of lane merge/splits with generators. See "highway_example_with_merge_and_split.py"
    - added __eq__ to all classes, (some limitations in the xodr module where the ids are generated)
    - scenario_generator got a new attribute (generate_all_roads), that if false will only generate unique roads (thanks to the __eq__   integration). See "generate_with_permutations.py"
    

### 2021-04-22 Version 0.3.4
- some documentation updates
- esmini path simplifications
- New Features
    - CatalogReader - new function in the xosc module, which can read a catalog and translate to a xosc object (works for Vehicle and Pedestrian in the first implementation)


### 2021-04-22 Version 0.3.3
- Bugfixes for esmini function
- New Features
    - Added support for laneOffset for Lanes


### 2021-04-22 Version 0.3.2
- Restructuring
    - All override controller actions (OverrideThrottleAction, OverrideBrakeAction, ...) are merged into one class, and the old ones are removed.
        

### 2021-04-20 Version 0.3.1
- New Features
    - type (road) support added
    - elevationprofile and lateral profile support added
    - junction group support added (no automation)
- Feature updates
    - initialDistanceOffset in FollowTrajectory added (OSC V1.1)
    - Geometires can now be added with x,y,h directly to a planview (not to mix with old functionality)
    - some small updates to the generators
    - esmini update to view the scenario with custom speed for run with replay
- Documentation updates

### 2021-03-25 Version 0.3.0
- Added relase notes.
    - before this, the pyoscx, pyodrx and scenariogeneration repos where joined and put on pypi
- Updates of documentation
- Some crash issues fixed.
- Typo in visibility action "traffic" is now correct