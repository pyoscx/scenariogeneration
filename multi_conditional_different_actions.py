""" Notes:
    An example showing how to setup a choise for one vehicle depending on what is happening around it, using multi conditions with different rules

    for different behaviour change speed_of_outer_car

    Some features used:
        ConditionGroup 
        TimeToCollisionCondition
        TimeHeadwayCondition
        AbsoluteSpeedAction
        AbsoluteLaneChangeAction
        Rule
        
"""
#change this to have different Ego behaviors (use 20 or 30)
speed_of_outer_car = 30


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

# change speed of this to have different outcome
init.add_init_action(speedyname,pyoscx.TeleportAction(pyoscx.LanePosition(10,0,-3,0)))
init.add_init_action(speedyname,pyoscx.AbsoluteSpeedAction(speed_of_outer_car,pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.step,pyoscx.DynamicsDimension.time,1)))

init.add_init_action(targetname,pyoscx.TeleportAction(pyoscx.LanePosition(100,0,-2,0)))
init.add_init_action(targetname,pyoscx.AbsoluteSpeedAction(10,pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.step,pyoscx.DynamicsDimension.time,1)))

### create the "optional" slowdown event

slowdown_event = pyoscx.Event('speedchange',pyoscx.Priority.overwrite)
slowdown_event.add_action('speedaction',pyoscx.AbsoluteSpeedAction(9,pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.sinusoidal,pyoscx.DynamicsDimension.time,1)))

# create two trigger conditions 
ttc_cond = pyoscx.TimeToCollisionCondition(3,pyoscx.Rule.lessThan,entity=targetname)
headway_cond = pyoscx.TimeHeadwayCondition(speedyname,1,pyoscx.Rule.lessThan)

headway_trigger = pyoscx.EntityTrigger('trigger',0,pyoscx.ConditionEdge.none,headway_cond,egoname)

collision_trigger = pyoscx.EntityTrigger('trigger',0,pyoscx.ConditionEdge.none,ttc_cond,egoname)

#create the "and" logic
sc_group = pyoscx.ConditionGroup()
sc_group.add_condition(collision_trigger)
sc_group.add_condition(headway_trigger)

slowdown_event.add_trigger(sc_group)

# create the optional lanechange event
lane_change_event = pyoscx.Event('lanechange',pyoscx.Priority.overwrite)

lane_change_event.add_action('lanechangeaction',pyoscx.AbsoluteLaneChangeAction(-3,pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.sinusoidal,pyoscx.DynamicsDimension.time,3)))


# create two separate condition groups
headway_cond_2 = pyoscx.TimeHeadwayCondition(speedyname,1,pyoscx.Rule.greaterThan)
headway_trigger_2 = pyoscx.EntityTrigger('trigger',0,pyoscx.ConditionEdge.none,headway_cond_2,egoname)

ttc_cond_2 = pyoscx.TimeToCollisionCondition(3,pyoscx.Rule.lessThan,entity=targetname)
collision_trigger_2 = pyoscx.EntityTrigger('trigger',0,pyoscx.ConditionEdge.none,ttc_cond_2,egoname)

lc_group = pyoscx.ConditionGroup()
lc_group.add_condition(headway_trigger_2)
lc_group.add_condition(collision_trigger_2)

lane_change_event.add_trigger(lc_group)



## create the storyboard
man = pyoscx.Maneuver('slow down maneuver')


man.add_event(slowdown_event)
man.add_event(lane_change_event)

sb = pyoscx.StoryBoard(init,pyoscx.ValueTrigger('stop_simulation',0,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(20,pyoscx.Rule.greaterThan),'stop'))
sb.add_maneuver(man,egoname)

## create the scenario
sce = pyoscx.Scenario('adaptspeed_example','User',paramdec,entities=entities,storyboard = sb,roadnetwork=road,catalog=catalog)

# display the scenario
pyoscx.prettyprint(sce.get_element())


pyoscx.esminiRunner(sce,esminipath='/home/mander76/local/scenario_creation/esmini')
