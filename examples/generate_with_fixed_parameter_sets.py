""" example of creating OpenSCENARIO and OpenDRIVE files with a fixed set of dictionaries that will generate the scenarios and roads

    Example usage: when very precise permutations of a scenario is wanted

    Will generate 2 different scenarios and roads.
"""

import pyodrx
import pyoscx
from scenariogeneration import ScenarioGenerator

class Scenario(ScenarioGenerator):
    def __init__(self):
        ScenarioGenerator.__init__(self)
        self.parameters = []
        d1 = {}
        d1['road_curvature'] = 0.001
        d1['speed'] = 10
        
        d2 = {}
        d2['road_curvature'] = 0.002
        d2['speed'] = 20
        
        self.parameters.append(d1)
        self.parameters.append(d2)
        self.naming = 'parameter'


    def road(self,**kwargs):

        road = pyodrx.create_road([pyodrx.Spiral(0.0000000001,kwargs['road_curvature'],100), pyodrx.Arc(kwargs['road_curvature'],50), pyodrx.Spiral(kwargs['road_curvature'],0.0000000001,100), pyodrx.Line(100)],id =0,left_lanes=2,right_lanes=2)
        odr = pyodrx.OpenDrive('myroad')
        odr.add_road(road)
        odr.adjust_roads_and_lanes()
        return odr

    def scenario(self,**kwargs):
        road = pyoscx.RoadNetwork(self.road_file)
        egoname = 'Ego'
        entities = pyoscx.Entities()
        entities.add_scenario_object(egoname,pyoscx.CatalogReference('VehicleCatalog','car_white'))

        catalog = pyoscx.Catalog()
        catalog.add_catalog('VehicleCatalog','../xosc/Catalogs/Vehicles')

        init = pyoscx.Init()

        init.add_init_action(egoname,pyoscx.TeleportAction(pyoscx.LanePosition(50,0,-2,0)))
        init.add_init_action(egoname,pyoscx.AbsoluteSpeedAction(kwargs['speed'],pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.step,pyoscx.DynamicsDimension.time,1)))

        event = pyoscx.Event('my event',pyoscx.Priority.overwrite)
        event.add_action('lane change',pyoscx.AbsoluteLaneChangeAction(-1,pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.sinusoidal,pyoscx.DynamicsDimension.time,4)))
        event.add_trigger(pyoscx.ValueTrigger('start_trigger ',0,pyoscx.ConditionEdge.none,pyoscx.SimulationTimeCondition(4,pyoscx.Rule.greaterThan)))

        man = pyoscx.Maneuver('maneuver')
        man.add_event(event)

        sb = pyoscx.StoryBoard(init,stoptrigger=pyoscx.ValueTrigger('start_trigger ',0,pyoscx.ConditionEdge.none,pyoscx.SimulationTimeCondition(13,pyoscx.Rule.greaterThan),'stop'))
        sb.add_maneuver(man,egoname)
        sce = pyoscx.Scenario('my scenario','Mandolin',pyoscx.ParameterDeclarations(),entities,sb,road,catalog)

        return sce

if __name__ == "__main__":
    s = Scenario()
    s.print_permutations()
    s.generate('my_scenarios')