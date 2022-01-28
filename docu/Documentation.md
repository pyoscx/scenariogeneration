Scenariogeneration is a python package created for easy creation and generation of the ASAM open standards: OpenSCENARIO and OpenDRIVE.

The package can be found on [pypi](https://pypi.org/project/scenariogeneration/), and the source-code on [github](https://github.com/pyoscx/scenariogeneration).

This user guide is ment for the package itself, not OpenSCENARIO nor OpenDRIVE, for more in depth documentation about the standards, please visit [ASAM](www.asam.net). 

Please note that this is not an official implementation of either OpenSCENARIO or OpenDRIVE. 

# Introduction

The package consists of the two main modules, __xosc__ (OpenSCENARIO), and __xodr__ (OpenDRIVE), together with some support functionality for auto generation with parametrization (ScenarioGenerator) as well as easy viewing with [esmini](https://github.com/esmini/esmini).

For detailed information about the packages please see the [documentation](scenariogeneration/index.html) page, where the submodules are described. 

For more indepth exampels, please see the [exampels](examples/index.html) page. The exampels can also be found on the [github](https://github.com/pyoscx/scenariogeneration/tree/main/examples) page.

For more detailed view of the new updates, please see the [release notes](https://github.com/pyoscx/scenariogeneration/blob/main/release_notes.md)

# The modules


## xosc

The __xosc__ module handles the parts related to OpenSCENARIO, and covers all of OpenSCENARIO V 1.0.0 and most of OpenSCENARIO V 1.1.0 (except the parts related to UserDefined things). The module is a xml file generator which allows the user to easily generate a full OpenSCENARIO hierarchy without the need of explicity define all the levels of abstraction (if not needed). This has led to a couple of name changes compared to the standard (mostly adding Absolute or Relative to the name), in the description of the class, the OpenSCENARIO references are written for reference.  

The idea with this module is to create easy access to the elements of OpenSCENARIO without having to expose the user to all the xml levels that does not carry any vital information for the user. Hence, some of the xml-elements that build up OpenSCENARIO are never seen in the class structure but compressed to a level where the user can set the required data. 

The module can generate xmls of both V1.0.0 and V1.1.0 of OpenSCENARIO.

In general the __xosc__ module does not contain many "smart" functionality (except some default values), but the user can build up the scenario based on the classes available. 

### Automatic generation of Story, Act, and ManeuverGroup

One of the few functionalities of the __xosc__ module is for simple scenario generation and to create the __StoryBoard__.

In short the __StoryBoard__, consists of alot of layers from the Story, down to the Actions and Triggers.
For simple scenarios the multiple top level layers (like Story, Act or ManeuverGroup) are not needed, hence the __StoryBoard__ has multiple ways of adding sub-classes (add_story, add_act, add_maneuvergroup, add_maneuver) and will generate the top levels to make the xml correct.

__NOTE:__ Do not use more than one of these calls (except add_story), because each call will create a new story, and this in most cases are not what a user would like.

### Generate different versions of OpenSCENARIO
As of scenariogeneration V0.5.0, it is possible to generate different versions of the resulting OpenSCENARIO xml.
This feature is enabled by one simple input to the Scenario class as:
```
sce = Scenario(... , osc_minor_version=0)
```
The default is 1 (V1.1.0), but with this V1.0.0 OpenSCENARIO xmls can be generated. 

The V1.1.0 will remove the depricated attributes, and have a pure V1.1.0 xml. If version specific elements are used together with the wrong version, a __OpenSCENARIOVersionError__ will be raised. 

NOTE: as of V0.5.0 some interfaces had to be changed in order to fulfill the V1.1.0 standard, please see the [release notes](https://github.com/pyoscx/scenariogeneration/blob/main/release_notes.md) for more info.

### Parsing an .xosc file and get the Python object back
As of scenariogeneration V0.7.0, the __xosc__ module supports parsing an existing .xosc file.
This enables modifying already exisisting xosc files, eg. from a Scenario editor.  

```
scenario = ParseOpenScenario('my_non_python_made_scenario.xosc')
```

__ParseOpenScenario__ can read all types of OpenSCENARIO files (Scenario, Catalog and ParameterValueDistribution), and will return the Object related to that file type. 

NOTE: more layers of classes are added in some cases, that the user don't usually see/use. Eg. the __ValueTrigger__ and __EntityTrigger__ will never be returned, but a __Trigger__ and __ConditionGroup__ will always be present. 

## xodr

The xodr module handles the part related to OpenDrive, and does not (as of now) have a full coverage of the standard, please see [coverage](https://github.com/pyoscx/scenariogeneration/blob/main/xodr_coverage.txt) for more information. 

The __xodr__ module is also a xml generator, similar to the __xosc__ module. However, since opendrive is more complicated to create a functional road-network, it includes a number of automation algorithms which allow the user to easily generate a correct OpenDRIVE hierarchy. As a matter of fact, the OpenDRIVE standard contains many geometrical dependencies, indexing, and complex structures, that to create the xml directly is quite cumbersome. Hence, it is highly recommended to use the automations and "generators" included in the package. In the examples, both "generator" level ([full_junction](examples/xodr/full_junction.html), [highway_example](examples/xodr/highway_example.html), and [simple_road_with_objects](examples/xodr/simple_road_with_objects.html)) and low level examples (as [junction_trippel_twoway](examples/xodr/junction_trippel_twoway.html), [multiple_geometries_one_road](examples/xodr/multiple_geometries_one_road.html) and [road_merge_w_lane_merge](exampels/xodr/road_merge_w_lane_merge.html) ) are presented. 

### Automatic calculation of geometries and links

The most important automation functionality is the *adjust_roads_and_lanes* method of the *OpenDRIVE* class, which does two main things:

1. **Patch all Geometries and Roads Together** This is done on two levels: the "RoadNetwork" level and the "PlanView" level. At the RoadNetwork level all defined roads are patched consecutively, and this is possible only if the "predecessor/successor" attributes of the roads have been set. This is done either by: fixing the first road added to (0,0,0) and patch all other roads to that one, or localize if any PlanView(s) created has a manually added start point (e.g. if multiple roads are not connected via predecessor/successor). At the PlanView level instead all geometries are patched together creating one continuous road, based at its start point. See the [highway_example](examples/xodr/highway_example.html) for an example showing how to work on the RoadNetwork level and [multiple_geometries_one_road](examples/xodr/multiple_geometries_one_road.html) for the PlanView level.

Note: *adjust_roads_and_lanes* will assume that the heading is continious between different geometries and roads.

2. **Create Lane Linking** At this step the algorithm tries to link the lanes between roads. Normally this requires the same number of lanes in the connecting roads, but if the roads have a different amount of lanes, (should only be done in a junction!), the algorithm handles this case by adding offsets when defining the predecessor/successor attributes (see example: [highway_example](examples/xodr/highway_example.html), or [direct_junction_exit](examples/xodr/direct_junction_exit.html))

__NOTE:__ No real sanity check is made with the *adjust_roads_and_lanes* method, hence the resulting road might be very strange if the input is "wrong". 

### Generators
For most simple roads, the generators that are provided in the __xodr__ module can be used. These most often will generate the roads that can build up the network and then the user can just "patch" them together with the "successor/predecessor" attributes (see [highway_example](examples/xodr/highway_example.html))

#### create_road
The *create_road* function is very useful to create rather simple roads with either fixed amount of lanes or simple lane-merge/splits. 
Some example usage of this can be seen in [highway_example](examples/xodr/highway_example.html).

#### create_cloth_arc_cloth
The  *create_cloth_arc_cloth* function creates road with a smooth curve based on a clothoid + arc + clothoid. This is often used since the curvature of the road will change continiously (and resulting in nice steering wheel changes for a driver).

#### create_3cloths
Similarly to *create_cloth_arc_cloth*, the *create_3cloths* function creates a smooth curve based on 3 consecutive spiral geoemtries (using pyclothoids)

#### create_junction_roads
- The *create_junction_roads* generates all the roads for a simple intersection. The position of roads around a junction is defined by *R*, the distance of each road form the center of the junction, and by *angles*, defining how the roads around the junction are spanned. With these inputs, *create_junction_roads* generates all the roads in the junction, which are connecting the surrounding roads. 

#### create_junction
The *create_junction* function creates the "junction" element of OpenDRIVE, based on a list of "roads in the junction" (that can be generated from *create_junction_roads*) and a list of "roads going into the junction" 

#### create_direct_junction
Similar to *create_junction*, create_direct_junction can be used to create the junction element for a direct junction. This is possible when using the direct_junction input in add_predecessor/add_successor, see [direct_junction_exit](examples/xodr/direct_junction_exit.html) or [direct_junction_entry](examples/xodr/direct_junction_entry.html)


#### LaneDef
LaneDef is a helper class that enables simple lane merge/split roads to be created, this definition can be used together with the create_road generator (see [highway_example_with_merge_and_split](examples/xodr/highway_example_with_merge_and_split.html)).

## ScenarioGenerator


The ScenarioGenerator class can be used as a glue to parametrize and generate connected OpenSCENARIO and OpenDRIVE xmls, for large scale, parametrized simulations (Note that a similar feature is supported in the OpenSCENARIO standard since V1.1.0).

To utilize this, let your Scenario class inherit ScenarioGenerator and initalize it. 
Some options can be used to parameterize your Scenario either by:
- let self.parameters be a dict containing lists. This in turn will yield all permutations of the inputs (Note: this grows quickly, so be careful)
- let self.parameters be a list of dicts (same structure in each element). This will yield a scenario for each entry in the list. 

Then overwrite the road and/or the scenario methods where the road should return an xodr.OpenDrive object, and the scenario method should return a xosc.Scenario object. 
To connect the scenario and the generated road, create the RoadNetwork object in the scenario as: xosc.RoadNetwork(self.road_file). 

Finally the *generate* method can be used to generate all permutations of the defined parameters.

### Useful ScenarioGenerator attributes
In the init of the Scenario, some of the attributes of the ScenarioGenerator can be set.

- *generate_all_road*: a boolean that will determine if one road per scenario should be generated, or that only unique roads will be created.

- *naming*: This will give the resulting generated .xmls different naming

    - 'numerical' - will give the scenarios a name with an increasing index for each generated permutation

    - 'parameter' - will give the parameters and their value in the filename (this will endup in very long names if alot of parameters are used)

# Useful Links
Useful links related to scenariogeneration

- [API documentation](scenariogeneration/index.html)

- [Exampels](examples/index.html)

- [release notes](https://github.com/pyoscx/scenariogeneration/blob/main/release_notes.md)

- [github](https://github.com/pyoscx/scenariogeneration)

- [pypi](https://pypi.org/project/scenariogeneration/)

Useful links for related projects and other information

- [ASAM](www.asam.net)

- [esmini](https://github.com/esmini/esmini)

- [pyclothoids](https://github.com/phillipd94/pyclothoids)

- [blender scenariogenerator](https://github.com/johschmitz/blender-driving-scenario-creator)
