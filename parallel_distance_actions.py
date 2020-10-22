""" Notes:
    Simple example showing how one vehicle triggers two different actions based on different distance related triggers

    Some features used:
        ReachPositionCondition
        RelativeDistanceCondition
        RelativeLaneChangeAction
        AbsoluteSpeedAction
"""

import pyoscx

### create catalogs
catalog = pyoscx.Catalog()
catalog.add_catalog('VehicleCatalog','../xosc/Catalogs/Vehicles')

### create road
road = pyoscx.RoadNetwork(roadfile='../xodr/e6mini.xodr',scenegraph='../models/e6mini.osgb')

### create parameters
paramdec = pyoscx.ParameterDeclarations()

## create entities

egoname = 'Ego'
egoref = 'Egofake'
targetname = 'Target'
entities = pyoscx.Entities()
entities.add_scenario_object(egoname,pyoscx.CatalogReference('VehicleCatalog','car_white'))
entities.add_scenario_object(targetname,pyoscx.CatalogReference('VehicleCatalog','car_yellow'))

### create init

init = pyoscx.Init()

init.add_init_action(egoname,pyoscx.TeleportAction(pyoscx.LanePosition(10,0,-4,0)))
init.add_init_action(egoname,pyoscx.AbsoluteSpeedAction(20,pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.step,pyoscx.DynamicsDimension.time,1)))

init.add_init_action(targetname,pyoscx.TeleportAction(pyoscx.LanePosition(50,0,-2,0)))
init.add_init_action(targetname,pyoscx.AbsoluteSpeedAction(10,pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.step,pyoscx.DynamicsDimension.time,1)))

## do lanechange
lc_cond = pyoscx.ReachPositionCondition(pyoscx.LanePosition(40,0,-4,0),1)
lc_event = pyoscx.Event('lanechange',pyoscx.Priority.parallel)
lc_event.add_action('lanechangeaction',pyoscx.RelativeLaneChangeAction(-1,targetname,pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.sinusoidal,pyoscx.DynamicsDimension.time,3)))
lc_event.add_trigger(pyoscx.EntityTrigger('lanechangetrigger',0,pyoscx.ConditionEdge.none,lc_cond,egoname))

event = pyoscx.Event('speedchange',pyoscx.Priority.parallel)
event.add_action('speedaction',pyoscx.AbsoluteSpeedAction(10,pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.linear,pyoscx.DynamicsDimension.time,3)))
trig_cond = pyoscx.RelativeDistanceCondition(5,pyoscx.Rule.lessThan,pyoscx.RelativeDistanceType.lateral,targetname)
event.add_trigger(pyoscx.EntityTrigger('trigger',0,pyoscx.ConditionEdge.none,trig_cond,egoname))

man = pyoscx.Maneuver('mymaneuver')
# man.add_event(lc_event)
man.add_event(event)

## create the storyboard
sb = pyoscx.StoryBoard(init,pyoscx.ValueTrigger('stop_simulation',0,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(20,pyoscx.Rule.greaterThan),'stop'))

sb.add_maneuver(man,egoname)
## create the scenario
sce = pyoscx.Scenario('adaptspeed_example','User',paramdec,entities=entities,storyboard = sb,roadnetwork=road,catalog=catalog)

# display the scenario
pyoscx.prettyprint(sce.get_element())


# pyoscx.esminiRunner(sce,esminipath='/home/mander76/local/scenario_creation/esmini')
