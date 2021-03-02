import pyoscx
import numpy as np

## example of parametrized EUNCAP2020 CCRb case


acceleration_time = 5

def CCRb(distance,decelleration):

    # create empty catalog
    catalog = pyoscx.Catalog()

    # add straight road
    road = pyoscx.RoadNetwork(roadfile='../xodr/straight_500m.xodr',scenegraph='../models/straight_500m.osgb')

    # create empty paramdeclaration
    paramdec = pyoscx.ParameterDeclarations()

    egoname = 'Ego'
    targetname = 'Target1'

    ### create vehicles
    ego_width = 2
    target_width = 1.8

    bb = pyoscx.BoundingBox(ego_width,5,1.8,2.0,0,0.9)
    fa = pyoscx.Axle(0.523598775598,0.8,1.68,2.98,0.4)
    ba = pyoscx.Axle(0.523598775598,0.8,1.68,0,0.4)
    white_veh = pyoscx.Vehicle('car_white',pyoscx.VehicleCategory.car,bb,fa,ba,69,10,10)

    white_veh.add_property_file('../models/car_white.osgb')
    white_veh.add_property('model_id','0')

    bb = pyoscx.BoundingBox(target_width,4.5,1.5,1.3,0,0.8)
    fa = pyoscx.Axle(0.523598775598,0.8,1.68,2.98,0.4)
    ba = pyoscx.Axle(0.523598775598,0.8,1.68,0,0.4)
    red_veh = pyoscx.Vehicle('car_red',pyoscx.VehicleCategory.car,bb,fa,ba,69,10,10)

    red_veh.add_property_file('../models/car_red.osgb')
    red_veh.add_property('model_id','2')

    ## create entities
    entities = pyoscx.Entities()
    entities.add_scenario_object(egoname,white_veh)
    entities.add_scenario_object(targetname,red_veh)


    # create init (0 starting speed)
    init = pyoscx.Init()
    step_time = pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.step,pyoscx.DynamicsDimension.time,1)
    
    # caluclate correct offset based on target vehicle width
    cal_offset = 0

    egospeed = pyoscx.AbsoluteSpeedAction(0,step_time)
    egostart = pyoscx.TeleportAction(pyoscx.LanePosition(25,cal_offset,-1,1))

    targetspeed = pyoscx.AbsoluteSpeedAction(0,step_time)
    targetstart = pyoscx.TeleportAction(pyoscx.LanePosition(25+distance,0,-1,1))

    init.add_init_action(egoname,egospeed)
    init.add_init_action(egoname,egostart)
    init.add_init_action(targetname,targetspeed)
    init.add_init_action(targetname,targetstart)

    # create start trigger
    trigger = pyoscx.ValueTrigger('starttrigger',0,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(1,pyoscx.Rule.greaterThan))

    # accelerate cars to wanted velocity
    eventego = pyoscx.Event('egospeedchange',pyoscx.Priority.overwrite)
    eventego.add_trigger(trigger)

    ego_action = pyoscx.AbsoluteSpeedAction(50/3.6,pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.linear,pyoscx.DynamicsDimension.time,acceleration_time))
    eventego.add_action('newspeed',ego_action)

    event_tar = pyoscx.Event('targetspeedchange',pyoscx.Priority.overwrite)
    event_tar.add_trigger(trigger)

    target_action = pyoscx.LongitudinalDistanceAction(-distance,egoname)
    event_tar.add_action('targetspeed',target_action)

    # trigger here could be changed to speed but tested for esmini at the point where speed condition was not implemented
    target_slowingdown_trigger = pyoscx.ValueTrigger('slowingdowntrigger',0,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(6,pyoscx.Rule.greaterThan))
    target_slowingdown_action = pyoscx.AbsoluteSpeedAction(0,pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.linear,pyoscx.DynamicsDimension.rate,abs(decelleration)))
    event_tar_slowdown = pyoscx.Event('target slowing down',pyoscx.Priority.overwrite)
    event_tar_slowdown.add_trigger(target_slowingdown_trigger)
    event_tar_slowdown.add_action('slowdownaction',target_slowingdown_action)

    # create maneuvers/maneuvergroups
    ego_man = pyoscx.Maneuver('ego man')
    ego_man.add_event(eventego)

    tar_man = pyoscx.Maneuver('target man')
    tar_man.add_event(event_tar)
    tar_man.add_event(event_tar_slowdown)
    

    egomangr = pyoscx.ManeuverGroup('egomangr')
    egomangr.add_actor(egoname)
    egomangr.add_maneuver(ego_man)

    tarmangr = pyoscx.ManeuverGroup('tarmangr')
    tarmangr.add_actor(targetname)
    tarmangr.add_maneuver(tar_man)

    # create act 
    act = pyoscx.Act('ccrm act',pyoscx.ValueTrigger('starttrigger',0,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(0,pyoscx.Rule.greaterThan)))

    act.add_maneuver_group(egomangr)
    act.add_maneuver_group(tarmangr)

    # create story
    story = pyoscx.Story('mystory')
    story.add_act(act)

    ## create the storyboard
    sb = pyoscx.StoryBoard(init,pyoscx.ValueTrigger('stop_simulation',2,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(acceleration_time + np.ceil(np.sqrt(2*distance/abs(decelleration))) + distance/50 ,pyoscx.Rule.greaterThan),'stop'))
    sb.add_story(story)

    ## create and return the scenario
    sce = pyoscx.Scenario('CCRb, distance: ' +str(distance) + ', decelleration: ' + str(decelleration),'Mandolin',paramdec,entities=entities,storyboard = sb,roadnetwork=road,catalog=catalog)
    return sce

if __name__ == '__main__':
    distance = [12, 40]
    decel = [-2,-6]
    sce = CCRb(distance[0],decel[0])
    # pyoscx.esminiRunner(sce)
