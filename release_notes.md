## scenariogeneration release notes

### 2025-10-16 Version 0.16.2
- General notes
    - Support for using "km/h". If you use "kph" it will be converted to "km/h" and you will get a Deprecation Warning.  
- Features
    - Add support for excluding specific permutations in scenario generation
- Bugfixes
    - Remove recursive call for stoptrigger


### 2025-09-22 Version 0.16.1
- Bugfixes
  - Fix deprecation warning during import.
  - Include the schemas in the wheel distribution.

### 2025-09-17 Version 0.16.0
- General notes
    - Implementation of OpenSCENARIO 1.3.1 is now complete.
- New features
    - XOSC:
      - TrafficActionArea
      - Polygon
      - RoadRange
      - ClothoidSpline
      - ClothoidSplineSegment
      - LogNormalDistribution
      - RandomRouteAction
      - Trailers
      - Monitor
      - AngleCondition
      - VerticalRoadSelection
      - ObjectController
    - XODR:
      - Object Marking for crosswalks, stop lines and parking spaces
- Bugfixes
    - Fix parsing issues related to OpenScenario version
    - Fix double fix-timestep entry in esmini runner
    - Fix bug in RelativeLaneOffsetAction
- Updates
    - Update action ActivateControllerAction to accept objectControllerRef
    - Properties are optional in most classes
    - Extend catalog FileHeader with more options
- Tests
    - Added tests for new features
    - Improved tests for existing features
    - Add schema checks in parser
- Optimization
    - Loose xmlschema requirement version
    - Trigger github action on schema

### 2025-07-03 Version 0.15.2
- Bugfixes
    - Fix in pyproject.toml for installation of dependencies.

### 2025-06-30 Version 0.15.1
- General notes
    - Updated documentation for creating artifacts and generating documentation for https://github.com/pyoscx/pyoscx.github.io
- Bugfixes
    - Fix in improved version handling during scenario parsing

### 2025-06-27 Version 0.15.0
- General notes
    - Docstrings have been updated to conform to the NumPy documentation standard.
    - Added test matrix for python versions in github workflows
- New features
    - New Black formatting
    - Switch to pyproject.toml
    - Typehinting
    - Add parsing of trajectory parameters
    - Parsing with different versions now handled better
- Bugfixes
    - Parser ParameterDeclarations in class Environment
    - ParseOpenScenario with encoding="utf-8"
    - (CommonJunctionCreator): offset handling in both circular and cartesian coord
    - Handling of deprication warning for ReachPositionCondition
    - General linting fixes
    - Version handling while parsing ActivateControllerAction
    - Fix bug when comparison of triggers didn't work after parsing when having stop-trigger 
- Test
    - Fix test for ReachPositionCondition depricated
- Examples
    - New example added for varable usage (see examples/xosc/variable_usage.py)

### 2024-12-04 Version 0.14.9
- New features
    - Extending Python version support. Now supporting 3.9-3.12.

### 2024-11-13 Version 0.14.8

- New features
    - Length parameter for signal objects
    - Information about road and junction IDs in AssertionError
    - xmlschema >= 3.3.1
- Bugfixes
    - fix lane link IDs
    - fix esmini runner replayer window size handling
    - fix coefficient value in lanewidth entry
- IMPORTANT!
    STD_ROADMARK_\<RoadMarkType\> has now been depricated and replaced with std_roadmark_\<RoadMarkType\>. 
    Please replace all references of constants to their function counterparts.

### 2024-09-02 Version 0.14.7

- New features
    LanePosition support roadId and and laneId of type string
- Bugfixes
    - fix issue with double quotation within double quotation
    - some typos

### 2024-08-28 Version 0.14.6

- New features
    - function add_lane_material
    - xmlschema version upgraded to 3.3.1
- Bugfixes
    - fix argument composition issues in esmini runner
    - fix missing child element for UserDefinedAction in class _Action parser
    - fix missing id four Outline in test_object that caused previous downgrade of xmlschema version

### 2024-06-17 Version 0.14.5

- New features
    - support space in esmini paths
- Bugfixes
    - add encoding in xosc_reader

### 2024-05-31 Version 0.14.4

- New features
    - support for geo_reference added. 
- Bugfixes
    - standard_lane allows user to set road mark parameter to None to not add a road mark

### 2024-01-24 Version 0.14.3

- New features
    - *adjust_elevation* tries to create fitted elevation profiles for roads without elevations.
    - type checks in xodr module (where applicable)
    - new base class for geometries in xodr module
- Bugfixes
    - LongitudinalDistanceAction now takes accelerationRate and decelerationRate as inputs
    - Type checks for AnimationAction fixed
    - Error in contact points for adjust_roadmarks fixed
- Tests
    - Tests for Exceptions for type errors added (both in xodr and xosc modules)
    - more tests for roadmark adjustment

### 2024-01-16 Version 0.14.2

- Bugfixes
  - STD_ROADMARK_SOLID now references solid RoadMarkType instead of broken
  - temporary fix: xmlschema pip package downgraded to version 2.5.1 due to unknown xsd validation failure
- New feature
  - Adjustable planview: can fit geometry between one predecessor and one successor road
- IMPORTANT!
  - Deprecation warning added for STD_ROADMARK_\<RoadMarkType\>, since only the functions std_roadmark_\<RoadMarkType\> will be supported in a future version. Please replace all references of constants to their function counterparts.


### 2023-12-20 Version 0.14.1

- Bugfixes
  - esmini_runner can now handle only odr from a ScenarioGenerator inherited class
  - bug fixed when using adjust_roads_and_lanes if a connecting road was the first added would fail,
  - JunctionCreator with circular geometry can now create straight lines again (introduced in 0.14.0)
- New feature
  - Some sanity checks for driving direction added. Both for connecting roads and in junctions, will throw a MixingDrivingDirection exception.
- Code structure
    - Catalog writing and ParameterDeclarations moved to _BaseCatalog superclass (all relevant classes updated)
- Tests
  - generators: more testing in creating lane merges and splits
  - JunctionCreators: a lot more tests covering more of the different ways of creating both common and direct junctions
  - OpenDrive class tested more for patching and when wrong input is given.
- Important!
  - Deprecation warnings added on old generation functions, such as create_straight_road, and old junction generation functions. All will be removed in a future release. Exampels are updated with no deprecated functions and new exampels for cases not covered in previous exampels.

### 2023-12-07 Version 0.14.0

- Bugfixes
  - DirectJunctionCreator can now handle successor-successor relations and predecessor-predecessor relations
  - Catalog references can be added directly to storyboard
- New feature
  - UserData implemented for xodr
  - Road linkage with different lane widths
  - LaneDef can generate lanes with individual lane widths
  - ParkingSpace type for OpenDRIVE object implemented
  - SignalReference element for OpenDRIVE implemented
  - Tunnel object for OpenDRIVE implemented
  - RoadMarkAdjustment new method in xodr module for adjusting broken lanemark (see example: xodr/road_with_lane_adjustment.py)
- Tests
  - all xodr classes and examples are validated against OpenDRIVE 1.7. Links and lane were updated to pass validation.


### 2023-10-05 Version 0.13.2

- Bugfixes
    - BoundingBox error for Fog
    - Fix so circular roads can be connected to a Junction
    - Fix for repeat objects for multiple lane sections
    - fixing som docstrings and error messages
- Optimization
    - More efficient "pretty print" when writing the xml files


### 2023-05-17 Version 0.13.1
- UserDefinedAction implemented correctly

### 2023-04-18 Version 0.13.0
- Bugfixes
    - encoding now works for all more options to write xmls
- New feature
    - xosc Enumeration handling has expanded,
        - can now handle parameters (with a "$" as first character)
        - input can now be strings (as long as they are the same as the enumeration name)
        - can parse parameters (with a "$" as first character)
- Important!
    - The exception types have been changed and more consistent for enumerations.

### 2023-03-22 Version 0.12.1

- New options for naming and generation
    - ScenarioGenerator class now has a base name that can be changed
    - naming option now has "parameter_no_list" which will give integer increase for lists

### 2023-03-10 Version 0.12.0
- General Notes
    - New tests
        - xsd tests for each class in the xosc module, as well for all the examples.
        - Testing xsd for OpenSCENARIO versions 1.0, 1.1, and 1.2
    - xosc examples encapsulated in ScenarioGenerator class to make testing easier

- Bugfixes
    - A lot of small fixes based on the xsd and version tests, including
        - typos in some elements
        - error handling when entries not related to a specific version is wanted

- IMPORTANT!
    - Interface changed for TimeOfDayCondition, now takes: year, month, day, hour, minute, second instead of a string as input

### 2023-02-23 Version 0.11.2
- Bugfixes
    - ParameterCondition fixed to handle all values


### 2023-02-10 Version 0.11.1
- Bugfixes
    - parametersetaction can now take non float values again
    - DistanceCondition can be created properly in V1.1 format

### 2023-02-02 Version 0.11.0
- Most of OpenSCENARIO V1.2.0 is implemented!
    - Still missing: Some UserDefined fields

- General notes:
    - Some extra inputs has been added to changed classes.
    - All ParameterActions/Condition has been replaced with VariableActions/Condition

- Some of the new features (will not write all new V1.2 features, check the official documentation):
    - AnimationAction
    - LightStateAction
    - SpeedProfileAction
    - RelativeClearanceCondition
    - VariableActions
    - More inputs to OverrideControllerValueAction
    - Multiple controllers can be added to entities
    - Roles
    - DirectionalDimension

- IMPORTANT!
    - osc_minor_version is now updated to 1.2, hence all scenarios will be on OpenSCENARIO V1.2 format, to make sure your previous scenarios keep the same version set the osc_minor_version in the Scenario constructor
    - FollowMode is now replaced with FollowingMode


### 2022-11-23 Version 0.10.1
- New Features
    - generate functions now have prettyprint input, having this false saves A LOT of time when generating large batches of scenarios. Example: for generating 10000 scenarios and roads, 42 seconds with pretty print 14 seconds without.


### 2022-11-17 Version 0.10.0
- New Features
    - esmini runner can now run in headless mode (without replay), with the headless input key
    - countryRevision added for Signals
    - __getitem__ introduced for xosc enums (Followmode['position'] now works)
    - parallelization of writing the xml files for ScenarioGenerator (useful for large generations)
- Bug Fixes
    - boolean checks updated so that parameterstrings on the format "$my_boolean_parameter" can be used in all xosc classes

### 2022-10-20 Version 0.9.3
- Bug Fixes
    - scenario_generator: if generate_single is used with int and the option numerical, the name will be that number

### 2022-10-14 Version 0.9.2
- Bug Fixes
    - Converting from 1.1 to 1.0 bug fixed.

### 2022-09-08 Version 0.9.1
- Bug Fixes
    - removal of non mandatory inputs to ActivateControllerAction
    - removal of unnecessary library

### 2022-07-01 Version 0.9.0
- New Features
    - outline can now be added for objects in opendrive
    - multiple lane widths and multiple roadmarks can be added for a Lane
    - method in lane to calculate the width at any s-coordinate
- Bug Fixes
    - maximumExecusion in event no longer required for parsing (according to the standard)
    - in Route position namings fixed to the correct names
-Changed Classes (API not changed, but if attributes are used this will brake some cases)
    - Lane
        - no longer have a, b, c, d, soffset as object attributes replaced with a list of a _poly3struct objects instead
        eg: previously to get the parameter a on the lane one would use _lane.a_, now _lane.widths[0].a_ should be used.

### 2022-06-10 Version 0.8.0
- New Features
    - all methods returns the object for oneliners
    - Junction creators added (replacing old junction functionality), see UserGuide.
        - Common and Direct junction creators added
    - LaneLinking functionality for roads with different amount of lanes
- Bug Fixes
    - Some lane-section linking fixes
    - connection offsets now take lane widths into account
- Cleaning up & testing
    - printing order of lanes and links
    - linking of roads more independent on the "add_road" order than previously (especially when dealing with junctions)
    - black standard applied
    - workflows for testing:
        - all examples scenarios/roads
        - black
        - pytest
-Changed Classes (IMPORTANT, Interface and Functionality Changed!)
    - Direct junction creation changed
        - old way of creating direct junctions was very buggy and only worked in a few cases.
        - add_successor/predecessor now does not have the direct_junction option
        - new DirectJunctionCreator should be used to be sure, will cover much more cases than the old one.

### 2022-03-30 Version 0.7.12
- order when parsing model/model3d updated

### 2022-03-29 Version 0.7.11
- Bug fixes
    - ParameterDeclarations had more bugs that were fixed.

### 2022-03-29 Version 0.7.10
- Bug fixes
    - ParameterDeclarations does not have to exist to parse a scenario.
    - cleaning up some duplicate functions
- New Feature
    - The sizes of Repeated Objects can now be set
- Documentation updates

### 2022-02-28 Version 0.7.9
- New Feature
    - create_junction_roads now have inputs to set the inner and outer (boarder) roadmarks
         - Default is changed: inside no roadmarks, boarder solid

### 2022-02-09 Version 0.7.8
- Bug fix in OverrideGearAction
- New Feature
    - license can now be added directly in the creation of Scenario
    - creation_date is added to file header if a custom date is wanted. (also as optional input to scenario)

### 2022-01-28 Version 0.7.6
- Bug fix in parsing along route

### 2022-01-27 Version 0.7.5
- Cleaning up some dependencies
    - removed some non-used libraries and dependencies
    - cleaning up imports
- New Features
    - booleans can now be parsed from "0" and "1"


### 2022-01-23 Version 0.7.4
- New Features
    - RoadMarks can now have multiple lines (for double road marks)

        - New standard roadmarks added for standard double roadmarks (solid-solid, solid-broken, broken-solid, and broken-broken)
        - new example how to create custom roadmarks
- Some updates to documentation

### 2022-01-17 Version 0.7.3
- Bug fix
    - removed some unnecessary printouts
    - fixed bug in parsing catalog for entities
    - the esmini runner can now set timestep without having to run headless
- New Features
    - Added better support for UserDefinedAction and CustonCommands
    - Direct junctions is now supported!
        - new funciton create_direct_junction (for the junction struct)
        - new input to add_successor/add_predecessor direct_junction to enable automation
        - examples for entry and exit added.
- New Classes
    - ControllerAction, now controller actions can be added within one element (required for 1.0), while parsing any controller action, this will be the return type.

### 2021-12-21 Version 0.7.2
- Bug fix
    - add_maneuvergroup could not handle a single actor being added.
    - typo fixes in precipitaton.
    - boundingbox for fog is no longer needed.

### 2021-12-17 Version 0.7.1
- Bug fix
    - Fixed bug when in CatalogLoader when loading with a CatalogReference

### 2021-12-16 Version 0.7.0
- New features
    - Parsing is here for OpenSCENARIO! Now a .xosc can be parsed and return the python object.
      This enables the user to modify an existing .xosc file easily in python.
      Note: It might not have the exact structure as it was created, eg. for triggers which will have both the Tigger and ConditionGroup present (so will never return an ValueTrigger or EntityTrigger object)
    - ValueConstraint and ValueConstraintGroup added, and can be added to Parameters
    - New CatalogLoader implemented, can now load a catalog and read multiple time from it without reloading the file. CatalogReader will still exist for a while but will be removed in future releases.
- Some properties changed (that were missing or should be optional)
- utf-8 encoding is now default, but can be changed as a new input to write functions.
- Changed Classes (IMPORTANT, Interface Changed!)
    - Some bugs were found in the implementation of OpenSCENARIO 1.1, hence some classes had to be changed.
        - Environment (removed wrong input name)
        - Pedestrian (made model optional)
        - LongitudinalTimegapAction is merged into LongitutinalDistanceAction (hence init is changed)


### 2021-10-12 Version 0.6.0
- New features
    - the esmini helper now creates it's own folder and do not generate scenarios in the esmini folder
      two additional inputs to set the generation folder aswell as a resource path for esmini
    - esmini osi input was changed, so not bool anymore, but a string (the name of the file)
- Bug fixes
    - checks for non-mandatory fields can now handle 0 (didn't before)

- Changed Classes (IMPORTANT, Interface Changed!)
    - AbosoluteSyncronizeAction and RelativeSyncronizeAction are removed and replaced with SyncronizeAction that handles both.
        - New classes related to the SyncronizeActions
            - AbsoluteSpeed
            - RelativeSpeedToMaster
            - TargetDistanceSteadyState
            - TargetTimeSteadyState

### 2021-09-10 Version 0.5.4
- New features
    - Support for ParameterValueDistribution type of xosc file.
        - All distributions (except UserDefinedDistribution) added
        - Example of how to write a parametrized scenario

### 2021-09-01 Version 0.5.3
- bug fix for enum for RHT and LHT
- enable setting of delimiter in generation of names

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