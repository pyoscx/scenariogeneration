""" Notes:
    Simple example showing how one vehicle triggers based on the speed of another vehcile, then changes it speed

    Some features used:
        SpeedCondition
        AbsoluteSpeedAction
        RoadPosition
        OffroadCondition
"""

import pyoscx   

### create catalogs
catalog = pyoscx.Catalog()
catalog.add_catalog('VehicleCatalog','../xosc/Catalogs/Vehicles')

### create road
road = pyoscx.RoadNetwork(roadfile='../xodr/e6mini.xodr',scenegraph='../models/e6mini.osgb')


### create parameters
paramdec = pyoscx.ParameterDeclarations()

paramdec.add_parameter(pyoscx.Parameter('$HostVehicle',pyoscx.ParameterType.string,'car_white'))
paramdec.add_parameter(pyoscx.Parameter('$TargetVehicle',pyoscx.ParameterType.string,'car_red'))

### create vehicles

bb = pyoscx.BoundingBox(2,5,1.8,2.0,0,0.9)
fa = pyoscx.Axle(0.523598775598,0.8,1.68,2.98,0.4)
ba = pyoscx.Axle(0.523598775598,0.8,1.68,0,0.4)
white_veh = pyoscx.Vehicle('car_white',pyoscx.VehicleCategory.car,bb,fa,ba,69,10,10)

white_veh.add_property_file('../models/car_white.osgb')
white_veh.add_property('model_id','0')


bb = pyoscx.BoundingBox(1.8,4.5,1.5,1.3,0,0.8)
fa = pyoscx.Axle(0.523598775598,0.8,1.68,2.98,0.4)
ba = pyoscx.Axle(0.523598775598,0.8,1.68,0,0.4)
red_veh = pyoscx.Vehicle('car_red',pyoscx.VehicleCategory.car,bb,fa,ba,69,10,10)

red_veh.add_property_file('../models/car_red.osgb')
red_veh.add_property('model_id','2')

## create entities

egoname = 'Ego'
targetname = 'Target'

entities = pyoscx.Entities()
entities.add_scenario_object(egoname,white_veh)
entities.add_scenario_object(targetname,red_veh)


### create init

init = pyoscx.Init()
step_time = pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.step,pyoscx.DynamicsDimension.time,1)

egospeed = pyoscx.AbsoluteSpeedAction(25,pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.sinusoidal,pyoscx.DynamicsDimension.time,8))
egostart = pyoscx.TeleportAction(pyoscx.LanePosition(25,0,-3,0))

targetspeed = pyoscx.AbsoluteSpeedAction(15,step_time)
targetstart = pyoscx.TeleportAction(pyoscx.RoadPosition(30,-5,0))

init.add_init_action(egoname,egospeed)
init.add_init_action(egoname,egostart)
init.add_init_action(targetname,targetspeed)
init.add_init_action(targetname,targetstart)


### create an event

trigcond = pyoscx.RelativeSpeedCondition(0,pyoscx.Rule.lessThan,egoname)

trigger = pyoscx.EntityTrigger('mytesttrigger',0.2,pyoscx.ConditionEdge.none,trigcond,targetname)

event = pyoscx.Event('myfirstevent',pyoscx.Priority.overwrite)
event.add_trigger(trigger)

sin_time = pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.linear,pyoscx.DynamicsDimension.time,5)
action = pyoscx.RelativeLaneChangeAction(-8,targetname,pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.linear,pyoscx.DynamicsDimension.time,6),-10)
event.add_action('newspeed',action)


## create the maneuver 
man = pyoscx.Maneuver('my_maneuver')
man.add_event(event)

mangr = pyoscx.ManeuverGroup('mangroup')
mangr.add_actor(targetname)
mangr.add_maneuver(man)
starttrigger = pyoscx.ValueTrigger('starttrigger',0,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(0,pyoscx.Rule.greaterThan))
act = pyoscx.Act('my_act',starttrigger)
act.add_maneuver_group(mangr)

## create the story
storyparam = pyoscx.ParameterDeclarations()
storyparam.add_parameter(pyoscx.Parameter('$owner',pyoscx.ParameterType.string,targetname))
story = pyoscx.Story('mystory',storyparam)
story.add_act(act)


## create the storyboard
stoptrigger = pyoscx.EntityTrigger('stop_simulation',0.5,pyoscx.ConditionEdge.rising,pyoscx.OffroadCondition(0.5),targetname,triggeringpoint='stop')
sb = pyoscx.StoryBoard(init,stoptrigger)
sb.add_story(story)

## create the scenario
sce = pyoscx.Scenario('adapt_speed_example','Mandolin',paramdec,entities=entities,storyboard = sb,roadnetwork=road,catalog=catalog)
# display the scenario
pyoscx.prettyprint(sce.get_element())

# if you want to save it
# sce.write_xml('myfirstscenario.xml',True)

# if you have esmini downloaded and want to see the scenario (add path to esmini as second argument)
# pyoscx.esminiRunner(sce,esminipath='/home/mander76/local/scenario_creation/esmini')