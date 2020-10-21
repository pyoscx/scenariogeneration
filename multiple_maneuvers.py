""" Notes:
    An example setting up multiple vehicles triggering on eachother and running in parallel

    Some features used:
        AbsoluteLaneChangeAction
        TimeHeadwayCondition
        
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
redname = 'Target1'
yelname = 'Target2'

entities = pyoscx.Entities()
entities.add_scenario_object(egoname,pyoscx.CatalogReference('VehicleCatalog','car_white'))
entities.add_scenario_object(redname,pyoscx.CatalogReference('VehicleCatalog','car_red'))
entities.add_scenario_object(yelname,pyoscx.CatalogReference('VehicleCatalog','car_yellow'))

### create init

init = pyoscx.Init()
step_time = pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.step,pyoscx.DynamicsDimension.time,1)

init.add_init_action(egoname,pyoscx.AbsoluteSpeedAction(30,step_time))
init.add_init_action(egoname,pyoscx.TeleportAction(pyoscx.LanePosition(25,0,-3,0)))
init.add_init_action(redname,pyoscx.AbsoluteSpeedAction(40,step_time))
init.add_init_action(redname,pyoscx.TeleportAction(pyoscx.LanePosition(15,0,-2,0)))
init.add_init_action(yelname,pyoscx.AbsoluteSpeedAction(30,step_time))
init.add_init_action(yelname,pyoscx.TeleportAction(pyoscx.LanePosition(35,0,-4,0)))

### create an event for the red car

r_trigcond = pyoscx.TimeHeadwayCondition(redname,0.1,pyoscx.Rule.greaterThan)
r_trigger = pyoscx.EntityTrigger('redtrigger',0.2,pyoscx.ConditionEdge.rising,r_trigcond,egoname)
r_event = pyoscx.Event('first_lane_change',pyoscx.Priority.overwrite)
r_event.add_trigger(r_trigger)
r_event.add_action('lane_change_red',pyoscx.AbsoluteLaneChangeAction(-4,pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.sinusoidal,pyoscx.DynamicsDimension.time,4)))


## create the act for the red car
r_man = pyoscx.Maneuver('red_maneuver')
r_man.add_event(r_event)

r_mangr = pyoscx.ManeuverGroup('mangroup_red')
r_mangr.add_actor(redname)
r_mangr.add_maneuver(r_man)

act = pyoscx.Act('red_act',pyoscx.ValueTrigger('starttrigger',0,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(0,pyoscx.Rule.greaterThan)))
act.add_maneuver_group(r_mangr)


## create an event for the yellow car


y_trigcond = pyoscx.TimeHeadwayCondition(redname,0.5,pyoscx.Rule.greaterThan)
y_trigger = pyoscx.EntityTrigger('yellow_trigger',0,pyoscx.ConditionEdge.rising,y_trigcond,yelname)

y_event = pyoscx.Event('yellow_lanechange',pyoscx.Priority.overwrite)
y_event.add_trigger(y_trigger)

y_event.add_action('lane_change_yellow',pyoscx.AbsoluteLaneChangeAction(-3,pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.sinusoidal,pyoscx.DynamicsDimension.time,2)))


## create the act for the yellow car
y_man = pyoscx.Maneuver('yellow_maneuver')
y_man.add_event(y_event)

y_mangr = pyoscx.ManeuverGroup('yellow_mangroup')
y_mangr.add_actor(yelname)
y_mangr.add_maneuver(y_man)
y_starttrigger = pyoscx.ValueTrigger('starttrigger',0,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(0,pyoscx.Rule.greaterThan))
# y_act = pyoscx.Act('my_act',y_starttrigger)
act.add_maneuver_group(y_mangr)


## create the story

story = pyoscx.Story('mystory')
story.add_act(act)
# story.add_act(y_act)

## create the storyboard
sb = pyoscx.StoryBoard(init,pyoscx.ValueTrigger('stop_simulation',0,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(10,pyoscx.Rule.greaterThan),'stop'))
sb.add_story(story)

## create the scenario
sce = pyoscx.Scenario('adaptspeed_example','Mandolin',paramdec,entities=entities,storyboard = sb,roadnetwork=road,catalog=catalog)

# display the scenario
pyoscx.prettyprint(sce.get_element())

# if you want to save it
# sce.write_xml('myfirstscenario.xml',True)

# if you have esmini downloaded and want to see the scenario
# pyoscx.esminiRunner(sce)