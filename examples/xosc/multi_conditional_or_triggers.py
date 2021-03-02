""" Notes:
    An example showing how a "or logic" for conditions can be created, and one action can be triggered on different conditions

    Some features used:
        ConditionGroup
        Trigger
        TimeToCollisionCondition
        TimeHeadwayCondition
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
speedyname = 'speedy_gonzales'
targetname = 'Target'
entities = pyoscx.Entities()
entities.add_scenario_object(egoname,pyoscx.CatalogReference('VehicleCatalog','car_white'))
entities.add_scenario_object(speedyname,pyoscx.CatalogReference('VehicleCatalog','car_blue'))
entities.add_scenario_object(targetname,pyoscx.CatalogReference('VehicleCatalog','car_yellow'))

### create init

init = pyoscx.Init()

init.add_init_action(egoname,pyoscx.TeleportAction(pyoscx.LanePosition(50,0,-2,0)))
init.add_init_action(egoname,pyoscx.AbsoluteSpeedAction(15,pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.step,pyoscx.DynamicsDimension.time,1)))

init.add_init_action(speedyname,pyoscx.TeleportAction(pyoscx.LanePosition(10,0,-3,0)))
init.add_init_action(speedyname,pyoscx.AbsoluteSpeedAction(30,pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.step,pyoscx.DynamicsDimension.time,1)))

init.add_init_action(targetname,pyoscx.TeleportAction(pyoscx.LanePosition(100,0,-2,0)))
init.add_init_action(targetname,pyoscx.AbsoluteSpeedAction(10,pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.step,pyoscx.DynamicsDimension.time,1)))

### create the action

event = pyoscx.Event('speedchange',pyoscx.Priority.overwrite)
event.add_action('speedaction',pyoscx.AbsoluteSpeedAction(10,pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.step,pyoscx.DynamicsDimension.time,3)))

# create two trigger conditions
trig_cond1 = pyoscx.TimeToCollisionCondition(2,pyoscx.Rule.lessThan,entity=targetname)
trig_cond2 = pyoscx.TimeHeadwayCondition(speedyname,1,pyoscx.Rule.greaterThan)

collision_trigger = pyoscx.EntityTrigger('trigger',0,pyoscx.ConditionEdge.none,trig_cond1,egoname)
headway_trigger = pyoscx.EntityTrigger('trigger',0,pyoscx.ConditionEdge.none,trig_cond2,egoname)

# create two separate condition groups

col_group = pyoscx.ConditionGroup()
col_group.add_condition(collision_trigger)

head_group = pyoscx.ConditionGroup()
head_group.add_condition(headway_trigger)

# create trigger and add the two conditiongroups (or logic)
trigger = pyoscx.Trigger()
trigger.add_conditiongroup(col_group)
trigger.add_conditiongroup(head_group)

event.add_trigger(trigger)

## create the storyboard
man = pyoscx.Maneuver('mymaneuver')
man.add_event(event)

sb = pyoscx.StoryBoard(init,pyoscx.ValueTrigger('stop_simulation',0,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(20,pyoscx.Rule.greaterThan),'stop'))
sb.add_maneuver(man,egoname)

## create the scenario
sce = pyoscx.Scenario('adaptspeed_example','User',paramdec,entities=entities,storyboard = sb,roadnetwork=road,catalog=catalog)

# display the scenario
pyoscx.prettyprint(sce.get_element())


# pyoscx.esminiRunner(sce,esminipath='/home/mander76/local/scenario_creation/esmini')
