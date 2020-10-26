""" Notes:
    An example showing how to create a trajector based on polyline 
    Also shows how to create a vehicle from start

    Some features used:
        RelativeLanePosition 
        Polyline
        Trajectory
        TimeHeadwayCondition
        FollowTrajectoryAction

        Vehicle
        BoundingBox
        Axel
        
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


bb = pyoscx.BoundingBox(2,5,1.8,2.0,0,0.9)
fa = pyoscx.Axel(30,0.8,1.68,2.98,0.4)
ba = pyoscx.Axel(30,0.8,1.68,0,0.4)
white_veh = pyoscx.Vehicle('car_white',pyoscx.VehicleCategory.car,bb,fa,ba,69,10,10)

white_veh.add_property_file('../models/car_white.osgb')
white_veh.add_property('model_id','0')


bb = pyoscx.BoundingBox(1.8,4.5,1.5,1.3,0,0.8)
fa = pyoscx.Axel(30,0.8,1.68,2.98,0.4)
ba = pyoscx.Axel(30,0.8,1.68,0,0.4)
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

egospeed = pyoscx.AbsoluteSpeedAction(30,step_time)
egostart = pyoscx.TeleportAction(pyoscx.LanePosition(25,0,-3,0))

targetspeed = pyoscx.AbsoluteSpeedAction(40,step_time)
targetstart = pyoscx.TeleportAction(pyoscx.LanePosition(15,0,-2,0))

init.add_init_action(egoname,egospeed)
init.add_init_action(egoname,egostart)
init.add_init_action(targetname,targetspeed)
init.add_init_action(targetname,targetstart)


### create an event

trigcond = pyoscx.TimeHeadwayCondition(targetname,0.4,pyoscx.Rule.greaterThan)

trigger = pyoscx.EntityTrigger('mytesttrigger',0.2,pyoscx.ConditionEdge.rising,trigcond,egoname)

event = pyoscx.Event('myfirstevent',pyoscx.Priority.overwrite)
event.add_trigger(trigger)

positionlist = []
positionlist.append(pyoscx.RelativeLanePosition(0,0,0,targetname))
positionlist.append(pyoscx.RelativeLanePosition(20,0.5,0,targetname))
positionlist.append(pyoscx.RelativeLanePosition(40,-0.5,0,targetname))
positionlist.append(pyoscx.RelativeLanePosition(60,-1,0,targetname))

polyline = pyoscx.Polyline([0,0.5,1,1.5],positionlist)


traj = pyoscx.Trajectory('my_trajectory','False')
traj.add_shape(polyline)



trajact = pyoscx.FollowTrajectoryAction(traj,pyoscx.FollowMode.position,pyoscx.ReferenceContext.relative,1,0)

event.add_action('newspeed',trajact)


## create the act
man = pyoscx.Maneuver('my_maneuver')
man.add_event(event)

mangr = pyoscx.ManeuverGroup('mangroup')
mangr.add_actor('$owner')
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
sb = pyoscx.StoryBoard(init)
sb.add_story(story)

## create the scenario
sce = pyoscx.Scenario('trajectory_example','Mandolin',paramdec,entities=entities,storyboard = sb,roadnetwork=road,catalog=catalog)
# display the scenario
pyoscx.prettyprint(sce.get_element())

# if you want to save it
# sce.write_xml('myfirstscenario.xml',True)

# if you have esmini downloaded and want to see the scenario (add path to esmini as second argument)
# pyoscx.esminiRunner(sce,esminipath='/home/mander76/local/scenario_creation/esmini')