"""
    An example showing how to create a trajector based on polyline
    Also shows how to create a vehicle from start

    Some features used:


    - SpeedProfileAction

"""
import os
from scenariogeneration import xosc, prettyprint

### create catalogs
catalog = xosc.Catalog()
catalog.add_catalog("VehicleCatalog", "../xosc/Catalogs/Vehicles")


### create road
road = xosc.RoadNetwork(
    roadfile="../xodr/e6mini.xodr", scenegraph="../models/e6mini.osgb"
)


### create parameters
paramdec = xosc.ParameterDeclarations()


## create entities

egoname = "Ego"
targetname = "Target"

entities = xosc.Entities()
entities.add_scenario_object(egoname, xosc.CatalogReference('VehicleCatalog','car_white'))
entities.add_scenario_object(targetname, xosc.CatalogReference('VehicleCatalog','car_red'))


### create init

init = xosc.Init()
step_time = xosc.TransitionDynamics(
    xosc.DynamicsShapes.step, xosc.DynamicsDimension.time, 0
)

egospeed = xosc.AbsoluteSpeedAction(20, step_time)
egostart = xosc.TeleportAction(xosc.LanePosition(25, 0, -3, 0))

targetspeed = xosc.AbsoluteSpeedAction(30, step_time)
targetstart = xosc.TeleportAction(xosc.LanePosition(15, 0, -2, 0))

init.add_init_action(egoname, egospeed)
init.add_init_action(egoname, egostart)
init.add_init_action(targetname, targetspeed)
init.add_init_action(targetname, targetstart)


### create an event
ego_event = xosc.Event('ego_speed_change',xosc.Priority.overwrite)
ego_event.add_trigger(xosc.ValueTrigger('sim_time_trigger',0,xosc.ConditionEdge.none,xosc.SimulationTimeCondition(1,xosc.Rule.greaterThan)))
ego_speed_change = xosc.SpeedProfileAction([20,30,25,40],xosc.FollowMode.follow,[0,5,10,20])
ego_event.add_action('ego_speed_change',ego_speed_change)
ego_man = xosc.Maneuver('ego_speed').add_event(ego_event)
## create the storyboard
sb = xosc.StoryBoard(init,xosc.ValueTrigger('sim_time_trigger',0,xosc.ConditionEdge.none,xosc.SimulationTimeCondition(30,xosc.Rule.greaterThan),'stop'))
sb.add_maneuver(ego_man,actors=egoname)

## create the scenario
sce = xosc.Scenario(
    "speed_profile_example",
    "Mandolin",
    paramdec,
    entities=entities,
    storyboard=sb,
    roadnetwork=road,
    catalog=catalog,
)

# Print the resulting xml
prettyprint(sce.get_element())

# write the OpenSCENARIO file as xosc using current script name
sce.write_xml(os.path.basename(__file__).replace(".py", ".xosc"))

# uncomment the following lines to display the scenario using esmini
# from scenariogeneration import esmini
# esmini(sce,os.path.join('esmini'))
