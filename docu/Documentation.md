Scenariogeneration is a python package created for easy creation and generation of the ASAM open standards: OpenSCENARIO and OpenDRIVE.

The package can be found on [pypi](https://pypi.org/project/scenariogeneration/), and the source-code on [github](https://github.com/pyoscx/scenariogeneration).

This user guide is ment for the package itself, not OpenSCENARIO nor OpenDRIVE, for more in depth documentation about the standards, please visit [ASAM](https://www.asam.net).

Please note that this is not an official implementation of either OpenSCENARIO or OpenDRIVE.

# Introduction

The package consists of the two main modules, __xosc__ (OpenSCENARIO), and __xodr__ (OpenDRIVE), together with some support functionality for auto generation with parametrization (ScenarioGenerator) as well as easy viewing with [esmini](https://github.com/esmini/esmini).

For detailed information about the packages please see the [documentation](scenariogeneration/index.html) page, where the submodules are described.

For more indepth exampels, please see the [exampels](examples/index.html) page. The exampels can also be found on the [github](https://github.com/pyoscx/scenariogeneration/tree/main/examples) page.

For more detailed view of the new updates, please see the [release notes](https://github.com/pyoscx/scenariogeneration/blob/main/release_notes.md)

# The modules


## xosc

The __xosc__ module handles the parts related to OpenSCENARIO, and covers all of OpenSCENARIO V 1.0.0 and most of OpenSCENARIO V 1.1.0 and OpenSCENARIO V 1.2.0. The module is a xml file generator which allows the user to easily generate a full OpenSCENARIO hierarchy without the need of explicity define all the levels of abstraction (if not needed). This has led to a couple of name changes compared to the standard (mostly adding Absolute or Relative to the name), in the description of the class, the OpenSCENARIO references are written for reference.

The idea with this module is to create easy access to the elements of OpenSCENARIO without having to expose the user to all the xml levels that does not carry any vital information for the user. Hence, some of the xml-elements that build up OpenSCENARIO are never seen in the class structure but compressed to a level where the user can set the required data.

The module can generate xmls of both V1.0.0, V1.1.0 and V1.2.0 of OpenSCENARIO.

In general the __xosc__ module does not contain many "smart" functionalities (except some default values), but the user can build up the scenario based on the classes available.

### Automatic generation of Story, Act, and ManeuverGroup

One of the few functionalities of the __xosc__ module is for simple scenario generation and to create the __StoryBoard__.

In short the __StoryBoard__, consists of alot of layers from the Story, down to the Actions and Triggers.
For simple scenarios the multiple top level layers (like Story, Act or ManeuverGroup) are not needed, hence the __StoryBoard__ has multiple ways of adding sub-classes (add_story, add_act, add_maneuvergroup, add_maneuver) and will generate the top levels to make the xml correct.

__WARNING:__ Do not use more than one of these calls (except add_story), because each call will create a new story, and this in most cases are not what a user would like.

### Generate different versions of OpenSCENARIO
As of scenariogeneration V0.5.0, it is possible to generate different versions of the resulting OpenSCENARIO xml.
This feature is enabled by one simple input to the Scenario class as:
```
sce = Scenario(... , osc_minor_version=0)
```
The default is 2 (V1.2.0), but with this V1.0.0 OpenSCENARIO xmls can be generated.

The V1.2.0 will remove the depricated attributes, and have a pure V1.2.0 xml. If version specific elements are used together with the wrong version, a __OpenSCENARIOVersionError__ will be raised.

NOTE: When a new versions of the standards are introduced, some interfaces might change, please see the [release notes](https://github.com/pyoscx/scenariogeneration/blob/main/release_notes.md) for more info.

### Parsing an .xosc file and get the Python object back
As of scenariogeneration V0.7.0, the __xosc__ module supports parsing an existing .xosc file.
This enables modifying already exisisting xosc files, eg. from a Scenario editor.

```
scenario = ParseOpenScenario('my_non_python_made_scenario.xosc')
```

__ParseOpenScenario__ can read all types of OpenSCENARIO files (Scenario, Catalog and ParameterValueDistribution), and will return the Object related to that file type.

__NOTE:__ more layers of classes are added in some cases, that the user don't usually see/use. Eg. the __ValueTrigger__ and __EntityTrigger__ will never be returned, but a __Trigger__ and __ConditionGroup__ will always be present. Same for the __StoryBoard__ that will contain all hierarcies from __Story__ down to Actions.

### Example usage of parsing and OpenSCENARIO versions

Sometimes you might recive a _.xosc_ file that is in a newer version than what your simulator needs, for this the _xosc_ module can be used to convert (if possible), to a older version like this:

```
from scenariogeneration import xosc

scenario = xosc.ParseOpenScenario("multiple_maneuvers_1.xosc")

scenario.header.setVersion(minor=0)

scenario.write_xml("multiple_maneuvers_0.xosc")
```

## xodr

The xodr module handles the part related to OpenDRIVE, and does not (as of now) have a full coverage of the standard, please see [coverage](https://github.com/pyoscx/scenariogeneration/blob/main/xodr_coverage.txt) for more information.

The __xodr__ module is also a xml generator, similar to the __xosc__ module. However, since OpenDRIVE is more complicated to create a functional road-network, it includes a number of automation algorithms which allow the user to easily generate a correct OpenDRIVE hierarchy. As a matter of fact, the OpenDRIVE standard contains many geometrical dependencies, indexing, and complex structures, that to create the xml directly is quite cumbersome. Hence, it is highly recommended to use the automations and "generators" included in the package. In the examples, both "generator" level ([full_junction](examples/xodr/full_junction.html), [highway_example](examples/xodr/highway_example.html), and [simple_road_with_objects](examples/xodr/simple_road_with_objects.html)) and low level examples (as [junction_trippel_twoway](examples/xodr/junction_trippel_twoway.html), [multiple_geometries_one_road](examples/xodr/multiple_geometries_one_road.html) and [road_merge_w_lane_merge](exampels/xodr/road_merge_w_lane_merge.html) ) are presented.

### Automatic calculation of geometries and links

The most important automation functionality is the *adjust_roads_and_lanes* method of the *OpenDRIVE* class, which does two main things:

1. **Patch all Geometries and Roads Together** This is done on two levels: the "RoadNetwork" level and the "PlanView" level. At the RoadNetwork level all defined roads are patched consecutively, and this is possible only if the "predecessor/successor" attributes of the roads have been set. This is done either by: fixing the first road added to (0,0,0) and patch all other roads to that one, or localize if any PlanView(s) created has a manually added start point (e.g. if multiple roads are not connected via predecessor/successor). At the PlanView level, instead all geometries are patched together creating one continuous road, based at its start point. See the [highway_example](examples/xodr/highway_example.html) for an example showing how to work on the RoadNetwork level and [multiple_geometries_one_road](examples/xodr/multiple_geometries_one_road.html) for the PlanView level.

__NOTE:__ *adjust_roads_and_lanes* will assume that the heading is continious between different geometries and roads.

2. **Create Lane Linking** At this step the algorithm tries to link the lanes between roads. Normally this requires the same number of lanes in the connecting roads, but if the roads have a different amount of lanes, (should only be done in a junction!), the algorithm handles this case by adding offsets when defining the predecessor/successor attributes (see example: [highway_example](examples/xodr/highway_example.html), or [direct_junction_exit](examples/xodr/direct_junction_exit.html))

__NOTE:__ No real sanity check is made with the *adjust_roads_and_lanes* method, hence the resulting road might be very strange if the inputs are "wrong".

### Generators
For most simple roads, the generators that are provided in the __xodr__ module can be used. These most often will generate the roads that can build up the network and then the user can just "patch" them together with the "successor/predecessor" attributes (see [highway_example](examples/xodr/highway_example.html))

#### create_road
The *create_road* function is very useful to create rather simple roads with either fixed amount of lanes or simple lane-merge/splits.
Some example usage of this can be seen in [highway_example](examples/xodr/highway_example.html).

#### create_cloth_arc_cloth
The  *create_cloth_arc_cloth* function creates road with a smooth curve based on a clothoid + arc + clothoid. This is often used since the curvature of the road will change continiously (and resulting in nice steering wheel changes for a driver).

#### create_3cloths
Similarly to *create_cloth_arc_cloth*, the *create_3cloths* function creates a smooth curve based on 3 consecutive spiral geoemtries (using [pyclothoids](https://github.com/phillipd94/pyclothoids))


#### LaneDef
LaneDef is a helper class that enables simple lane merge/split roads to be created, this definition can be used together with the create_road generator (see [highway_example_with_merge_and_split](examples/xodr/highway_example_with_merge_and_split.html)).

### JunctionCreators

Since version 0.8.0 the xodr module contains two JunctionCreators. The JunctionCreators replaces the create_junction, create_direct_junction, and create_junction_roads, which had some limmitations when it came to create custom junctions.

#### CommonJunctionCreator
The *CommonJunctionCreator* is the class that helps the user to create the *common* junctions in OpenDRIVE, this is done in two steps: (1) adding the road to connect to the junction and its position, (2) adding connections between roads and optionally lanes.

First of all, the roads needs a predecessor or successor pointing to the junction. This can be done in two different ways: (1) with the *add_successor/add_predecessor*, or (2) with the *add_incoming_road* functions in the junction creator.

When adding a road to the junction two functions are available, *add_incoming_road_cartesian_geometry* and *add_incoming_road_circular_geometry*, both uses a local coordinate system for that junciton that will help to connect the roads together.
- The *add_incoming_road_cartesian_geometry* uses a *x-y* coordinate system with an arbitrary origin, the incomming road is added with an *x-y-h* input, where *h* is the heading of the road __into__ the junction.

![Cartesian](https://github.com/pyoscx/scenariogeneration/blob/main/docu/cartesian.png?raw=true "Cartesian geometry")

- The *add_incoming_road_circular_geometry* uses a *r-h* coordinate system where the origin is in the middle of the junction and *r* is the radius and *h* the heading from the center where to connect the road.


![Circular](https://github.com/pyoscx/scenariogeneration/blob/main/docu/circular.png?raw=true "Circular geometry")




An example can be seen below:
```
from scenariogeneration import xodr

road1 = xodr.create_road(xodr.Line(100), id=1, left_lanes=2, right_lanes=2)
road2 = xodr.create_road(xodr.Line(100), id=2, left_lanes=1, right_lanes=1)
road3 = xodr.create_road(xodr.Line(100), id=3, left_lanes=2, right_lanes=2)

junction_creator = xodr.CommonJunctionCreator(id = 100, name='my_junction')

junction_creator.add_incoming_road_cartesian_geometry(road1,
            x = 0,
            y = 0,
            heading=0,
            road_connection='successor')

junction_creator.add_incoming_road_cartesian_geometry(road2,
            x = 50,
            y = 50,
            heading=3.1415*3/2,
            road_connection='predecessor')

junction_creator.add_incoming_road_cartesian_geometry(road3,
            x = 100,
            y = 0,
            heading=-3.1415,
            road_connection='predecessor')

```

With all the roads added to the junction, connections can be added using the *add_connection* method. The minimum input of the *add_connection* method is the road ids (in the example above 1 and 2). This will generate a connecting road with the minimum equal number of lanes between the two roads (in the example above a road with one left and one right lanes). And simultaneously create the entries in the _junction_ element.

In some cases only some lanes should be connected between two roads, then the optional parameters to the *add_connection* method can be used, specifying the lanes that should be connected. This will generate a connecting road just between those two lanes.

Continuing the example above:

```
junction_creator.add_connection(road_one_id = 1,
                                road_two_id = 3)

junction_creator.add_connection(road_one_id = 1,
                                road_two_id = 2,
                                lane_one_id = 2,
                                lane_two_id = 1)

junction_creator.add_connection(road_one_id = 2,
                                road_two_id = 3,
                                lane_one_id = -1,
                                lane_two_id = 2)

```

Finally the roads and junction have to be added to the *OpenDrive* object, and for simplicity, the *add_junction_creator* can be used.
The final part of the example will look like this


```
odr = xodr.OpenDrive('myroad')

odr.add_road(road1)
odr.add_road(road2)
odr.add_road(road3)

odr.add_junction_creator(junction_creator)
odr.adjust_roads_and_lanes()

```
#### DirectJunctionCreator

To create *direct* type of junctions, the DirectJunctionCreator can be used. Since a *DirectJunction* has no need to generate roads in the junction, no geometrical description is needed. For each road connected to the *DirectJunction*, the successor/predecessor has to be added with the add_successor/add_predecessor methods.
An example can be se below:



```
from scenariogeneration import xodr
junction_id = 100
direct_junction = xodr.DirectJunctionCreator(junction_id,'my_direct_junction')

first_road = xodr.create_road([xodr.Line(300)],
            id= 1,
            left_lanes=3,
            right_lanes=4)

continuation_road = xodr.create_road([xodr.Line(300)],
            id= 2,
            left_lanes=3,
            right_lanes=3)

off_ramp = xodr.create_road([xodr.Spiral(-0.00001,-0.02,length=150)],
            id= 3,
            left_lanes=0,
            right_lanes=1)

first_road.add_successor(xodr.ElementType.junction, junction_id)
continuation_road.add_predecessor(xodr.ElementType.junction, junction_id)
off_ramp.add_predecessor(xodr.ElementType.junction, junction_id)
```

To create the connections in the *DirectJunction* the *add_connection* method is used, taking the road objects as inputs. To connect only certain lanes, the optional inputs *incoming_lane_id* and *linked_lane_id* parameters.

An example (continuation of the example above):

```
direct_junction.add_connection(
            incoming_road = first_road,
            linked_road = continuation_road)
direct_junction.add_connection(
            incoming_road = first_road,
            linked_road = off_ramp,
            incoming_lane_id=-4,
            lined_lane_id = -1)
```
and finally adding the roads to opendrive:

```
odr = xodr.OpenDrive('myroad')

odr.add_road(road1)
odr.add_road(road2)
odr.add_road(road3)

odr.add_junction_creator(junction_creator)
odr.adjust_roads_and_lanes()

```

## ScenarioGenerator


The ScenarioGenerator class can be used as a glue to parametrize and generate connected OpenSCENARIO and OpenDRIVE xmls, for large scale, parametrized simulations (In the OpenSCENARIO standard since V1.1.0, this is included in the standard).

To utilize this, let your Scenario class inherit ScenarioGenerator and initalize it.
Some options can be used to parameterize your Scenario either by:
- let self.parameters be a dict containing lists. This in turn will yield all permutations of the inputs (__WARBUBG:__ this grows quickly, so be careful)
- let self.parameters be a list of dicts (same structure in each element). This will yield a scenario for each entry in the list.

Then implement the road and/or the scenario methods where the road should return an xodr.OpenDrive object, and the scenario method should return a xosc.Scenario object.
To connect the scenario and the generated road, create the RoadNetwork object in the scenario as: xosc.RoadNetwork(self.road_file).

Finally the *generate* method can be used to generate all permutations of the defined parameters.

### Useful ScenarioGenerator attributes
In the init of the Scenario, some of the attributes of the ScenarioGenerator can be set.

- *generate_all_road*: a boolean that will determine if one road per scenario should be generated, or that only unique roads will be created.

- *naming*: This will give the resulting generated .xmls different naming

    - 'numerical' - will give the scenarios a name with an increasing index for each generated permutation

    - 'parameter' - will give the parameters and their value in the filename (this will endup in very long names if alot of parameters are used)

    - 'parameter_no_lists' - will give parameter and their value, except if the value is a list, then an integrer will be set instead (like numerical)

- *number_of_parallel_writings*: an integrer that will tell how many parallel processes should be used to write the xml files.

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
