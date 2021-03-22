# scenariogeneration

The Python scenariogeneration package is a collection of libraries for generating OpenSCENARIO (.xosc) and OpenDRIVE (.xodr) XML files.

This combined package (which includes the former pyoscx, pyodrx) can be used to jointly generate OpenSCENARIO based scenarios with interlinked OpenDRIVE based road network maps. Nevertheless, it is still possible to separately generate OpenSCENARIO or OpenDRIVE files by using only a subset of the provided functionality.

The package consists of the __scenario_generator__ module and two  Python subpackages, __xosc__ (OpenSCENARIO) and __xodr__ (OpenDRIVE), together with some support functionality for auto generation with parametrization as well as easy viewing with [esmini](https://github.com/esmini/esmini).

The package documentation can be found here: https://pyoscx.github.io/

Please note that this is not an official implementation of either OpenSCENARIO or OpenDRIVE. 

## Coverage

As of V0.2.0, the coverage of the modules varies:
- The xosc module has full coverage of OpenSCENARIO (V 1.0.0), if something is missing please raise an issue.
- The xodr module has coverage of basic roads, junctions, signals, and objects, based on OpenDrive (V 1.5.0). 

For more details se xodr_coverage.txt

## Getting Started

pip install scenariogeneration

then run any of the examples provided

### Prerequisites

Been tested with Python >3.6.9

### Installing

```
pip install scenariogeneration
```

## Usage

### xosc

The xosc module handles the part related to OpenSCENARIO, and covers all of OpenSCENARIO (V 1.0.0). The module is a xml file generator which allows the user to easily generate a full OpenSCENARIO hierarchy without the need of explicity define all the levels of abstraction (if not needed). 

### xodr

The xodr module handles the part related to OpenDrive, and does not (as of now) have a full coverage of the standard, please see coverage.txt for more information. 

The xodr module is also a xml generater, similar to the xosc module. It includes a number of automation algorithms which allow the user to easily generate the OpenDRIVE hierarchy. As a matter of fact the OpenDRIVE standard contains many geometrical dependencies, indexing, and complex structures, therefore a collection of automations (geometrical calculations and index linking), and road generators (to generate simple roads with different geometries and lanes) are included in the module.

The most important automation functionality is the *adjust_roads_and_lanes* method of the *OpenDRIVE* class, which does two main things:
    
1. **Patch all Geometries and Roads Together** This is done on two levels: the "RoadNetwork" level and the "PlanView" level. At the RoadNetwork level all defined roads are patched consecutively, and this is possible only if the "predecessor/successor" attributes of the roads have been set. This is done either by: fixing the first road added to (0,0,0) and patch all other roads to that one, or localize if any PlanView(s)  created has a manually added start point (e.g. if multiple roads are not connected via predecessor/successor). At the PlanView level instead all geometries are patched together creating one continuous road, based at its start point. See [examples/xodr/highway_example.py](examples/xodr/highway_example.py) for an example showing how to work on the RoadNetwork level and [examples/xodr/multiple_geometries_one_road.py](examples/xodr/multiple_geometries_one_road.py) for the PlanView level.

2. **Create Lane Linking** At this step the algorithm tries to link the lanes between roads. Normally this requires the same number of lanes in the connecting roads, but if the roads have a different amount of lanes, (should only be done in a junction!), the algorithm handles this case by adding offsets when defining the predecessor/successor attributes (see example: highway_example)

The xodr module also includes road generators which allow the user to create some standard cases in a faster and friendly way.
- *create_road* generates simple roads with different geometries and different number of lanes on each side. (see highway_example)
- *create_cloth_arc_cloth* creates road with a smooth curve based on a clothoid + arc + clothoid. 
- *create_junction* creates the junction element of OpenDRIVE, based on a list of "roads in the junction" and a list of "roads going into the junction" (see highway_example)
- *create_junction_roads* generates all roads in a simple 3 or 4 way (90 deg, and 120 deg in 3 way) junction (see full_junction)

### The ScenarioGenerator

The ScenarioGenerator class can be used as a glue to parametrize and generate connected OpenSCENARIO and OpenDRIVE xmls, for large scale, parametrized simulations. 

To utilize this, let your Scenario class inherit ScenarioGenerator and initalize it. 
Some options can be used to parameterize your Scenario either by:
- let self.parameters be a dict containing lists. This in turn will yield all permutations of the inputs (Note: this grows quickly, so be careful)
- let self.parameters be a list of dicts (same structure in each element). This will yield a scenario for each entry in the list. 

Then overwrite the road and/or the scenario methods where the road should return an xodr.OpenDrive object, and the scenario method should return a xosc.Scenario object. 
To connect the two, create the RoadNetwork object as: xosc.RoadNetwork(self.road_file). 

Finally the *generate* method can be used to generate all permutations of the defined parameters. See example below. 

```
from scenariogeneration import xosc
from scenariogeneration import xodr

from scenariogeneration import ScenarioGenerator


class Scenario(ScenarioGenerator):
    def __init__(self):
        ScenarioGenerator.__init__(self)

        self.parameters['road_curvature'] = [0.001, 0.002, 0.003, 0.004]
        self.parameters['speed'] = [10, 20, 30]
        self.naming = 'numerical'

    def road(self,**kwargs):
        # create a simple road
        road = xodr.create_road([xodr.Spiral(0.0000000001,kwargs['road_curvature'],100), xodr.Arc(kwargs['road_curvature'],50), xodr.Spiral(kwargs['road_curvature'],0.0000000001,100), xodr.Line(100)],id =0,left_lanes=2,right_lanes=2)
        odr = xodr.OpenDrive('myroad')
        odr.add_road(road)
        odr.adjust_roads_and_lanes()
        return odr

    def scenario(self,**kwargs):
        # create a simple scenario
        road = xosc.RoadNetwork(self.road_file)
        egoname = 'Ego'
        entities = xosc.Entities()
        entities.add_scenario_object(egoname,xosc.CatalogReference('VehicleCatalog','car_white'))

        catalog = xosc.Catalog()
        catalog.add_catalog('VehicleCatalog','../xosc/Catalogs/Vehicles')

        init = xosc.Init()

        init.add_init_action(egoname,xosc.TeleportAction(xosc.LanePosition(50,0,-2,0)))
        init.add_init_action(egoname,xosc.AbsoluteSpeedAction(kwargs['speed'],xosc.TransitionDynamics(xosc.DynamicsShapes.step,xosc.DynamicsDimension.time,1)))

        event = xosc.Event('my event',xosc.Priority.overwrite)
        event.add_action('lane change',xosc.AbsoluteLaneChangeAction(-1,xosc.TransitionDynamics(xosc.DynamicsShapes.sinusoidal,xosc.DynamicsDimension.time,4)))
        event.add_trigger(xosc.ValueTrigger('start_trigger ',0,xosc.ConditionEdge.none,xosc.SimulationTimeCondition(4,xosc.Rule.greaterThan)))

        man = xosc.Maneuver('maneuver')
        man.add_event(event)

        sb = xosc.StoryBoard(init,stoptrigger=xosc.ValueTrigger('start_trigger ',0,xosc.ConditionEdge.none,xosc.SimulationTimeCondition(13,xosc.Rule.greaterThan),'stop'))
        sb.add_maneuver(man,egoname)
        sce = xosc.Scenario('my scenario','Mandolin',xosc.ParameterDeclarations(),entities,sb,road,catalog)

        return sce

if __name__ == "__main__":
    s = Scenario()
    
    s.generate('my_scenarios')
```

### Running with esmini

Esmini can be used to visualize the generated scenarios. Visit https://github.com/esmini/esmini and follow the "Binaries and demos" section.
Your scenarios can be visualized directly by making use of *esminiRunner* in the following way:

```
from scenariogeneration import esmini

def Scenario(ScenarioGenerator): ...


s = Scenario()
if __name__ == "__main__":
    s = Scenario()
    
    esmini(s,esminipath ='path to esmini', index_to_run = 'first')
```
where *index_to_run* can be 'first', 'random', 'middle' or an integer, and esmini will run that scenario/road for you.

## Related work

### esmini

[esmini](https://github.com/esmini/esmini) is a basic OpenSCENARIO player

### spirals

[pyeulerspiral](https://github.com/stefan-urban/pyeulerspiral), used this lib for calculating euler spirals

## Authors

* **Mikael Andersson** - *Initial work* - [MandolinMicke](https://github.com/MandolinMicke) (xosc & xodr)

* **Irene Natale** - *Inital work* - [inatale93](https://github.com/inatale93) (xodr)

## Data formats

The wrappers is based on the OpenSCENARIO and OpenDRIVE standards.

[OpenDRIVE](https://www.asam.net/standards/detail/opendrive/)

describes the static content of a scenario, like the road, lanes, signs and so on.

[OpenSCENARIO](https://www.asam.net/standards/detail/openscenario/)

describes the dynamic content on top of a road network, e.g. traffic maneuvers, weather conditions, and so on.

