## scenariogeneration release notes

### 2021-08-26 Version 0.5.2
- added enum for RHT and LHT
- Some residual old clothoid calculations removed

### 2021-08-23 Version 0.5.1
- Bug fixes for V1.1.0 implmentation
- Switch to pyclothoid for clothoid calculations

### 2021-07-02 Version 0.5.0
- Most of OpenSCENARIO V1.1.0 is implemented!
    - Still missing: everything related to ParameterValueDistributionDefinition

- Some general notes:
    - Some extra inputs are added to the changed classes (to many to write out here), none are however removed (except the classes that has been changed, see below)
    - "alongroute" is replaced by CoordinateSystem and a displacement

- Some new features (OpenScenario V1.1.0):
    - TrajectoryPosition
    - GeoPosition
    - ExternalObjectReference
    - License
    - Wind
    - TargetDistanceSteadyState
    - TargetTimeSteadyState
    - TrafficStopAction
    - CoordinateSystem
    - LateralDisplacement
    - LongitudinalDisplacement

- New features (scenariogeneration)
    - New exceptions - to take care of different versions of OpenSCENARIO (will throw exceptions if V1.0.0 is wanted but trying to use features from V1.1.0)
    - VersionBase - new base class to handle different versions of OpenSCENARIO
 
    - the class Scenario has a new input "osc_minor_version" which enables the user to generate both OpenSCENARIO V1.0.0 and V1.1.0 type of files (V1.1.0 is default)

- Changed Classes (IMPORTANT, Interface Changed!)
    - In order to hande some changes in V1.1.0 two classes has be changed, and the user is recommended to update accordingly. This was neccesary to handle new optional inputs.
        - RelativeLanePosition - New input optional dsLane made ds also optional, and the order of the inputs had to be changed (updated to ds instead of s aswell)
            - previous init: __init__(self,s,offset,lane_id,entity,orientation=Orientation()):
            - new init: __init__(self,lane_id,entity,offset=0,ds=None,dsLane=None,orientation=Orientation())
        - Weather - all inputs are now optional to the weather element, and new classes were created for each subelement.
            - previous init: __init__(self,cloudstate,sun_intensity,sun_azimuth,sun_elevation,precipitation,precipitation_intensity,visual_fog_range = 100000,fog_bounding_box = None)
            - new init: __init__(self,cloudstate=None,atmosphericPressure=None,temperature=None,sun=None,fog=None,precipitation=None,wind=None)
            - New classes created to be used in the weather element:
                - Fog
                - Sun
                - Precipitation
                - Wind 
    - Enum is no longer used, but replaced with _OscEnum which helps with the versioning of OpenSCENARIO, main difference is that to get the enum name, use .get_name() instead of .name

### 2021-06-10 Version 0.4.0
- update of generators
   - create_junction_roads now uses R (distance from the center of the junction to the roads), instead of r (the radius of the arc that made the connecting road)
   - create_junction_roads can now handle any angles and any amount of roads going in to the junction, will assume a circle (radius R) to fit the roads into. 
- big documentation update, new page, including examples in online documentation.
- road-road linking generalized so roads can be added as successor/successor or predecessor/predecessor pairs.
- bug fix
   - it was possible to add multiple lane links, this is fixed, now only one successor/predecessor is alowed. 

### 2021-05-28 Version 0.3.7
- bug fix for Arcs

### 2021-05-28 Version 0.3.6
- update of order of elements in Road to fulfill xsd

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