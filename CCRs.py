import pyoscx


## example of parametrized EUNCAP2020 CCRs case

ttc_at_speed = 4
acceleration_time = 5

def CCRs(ego_speedvalue,offset):
    
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
    fa = pyoscx.Axel(30,0.8,1.68,2.98,0.4)
    ba = pyoscx.Axel(30,0.8,1.68,0,0.4)
    white_veh = pyoscx.Vehicle('car_white',pyoscx.VehicleCategory.car,bb,fa,ba,69,10,10)

    white_veh.add_property_file('../models/car_white.osgb')
    white_veh.add_property('model_id','0')

    bb = pyoscx.BoundingBox(target_width,4.5,1.5,1.3,0,0.8)
    fa = pyoscx.Axel(30,0.8,1.68,2.98,0.4)
    ba = pyoscx.Axel(30,0.8,1.68,0,0.4)
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
    cal_offset = offset/100*target_width

    egospeed = pyoscx.AbsoluteSpeedAction(0,step_time)
    egostart = pyoscx.TeleportAction(pyoscx.LanePosition(25,cal_offset,-1,1))

    startpos = 25 + ego_speedvalue/3.6* (acceleration_time+ttc_at_speed)
    targetspeed = pyoscx.AbsoluteSpeedAction(0,step_time)
    targetstart = pyoscx.TeleportAction(pyoscx.LanePosition(startpos,0,-1,1))

    init.add_init_action(egoname,egospeed)
    init.add_init_action(egoname,egostart)
    init.add_init_action(targetname,targetspeed)
    init.add_init_action(targetname,targetstart)

    # create start trigger
    trigger = pyoscx.ValueTrigger('starttrigger',0,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(1,pyoscx.Rule.greaterThan))

    # accelerate cars to wanted velocity
    eventego = pyoscx.Event('egospeedchange',pyoscx.Priority.overwrite)
    eventego.add_trigger(trigger)

    ego_action = pyoscx.AbsoluteSpeedAction(ego_speedvalue/3.6,pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.linear,pyoscx.DynamicsDimension.time,acceleration_time))
    eventego.add_action('newspeed',ego_action)


    # create maneuvers/maneuvergroups
    ego_man = pyoscx.Maneuver('ego man')
    ego_man.add_event(eventego)

    egomangr = pyoscx.ManeuverGroup('egomangr')
    egomangr.add_actor(egoname)
    egomangr.add_maneuver(ego_man)


    # create act 
    act = pyoscx.Act('ccrm act',pyoscx.ValueTrigger('starttrigger',0,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(0,pyoscx.Rule.greaterThan)))

    act.add_maneuver_group(egomangr)

    # create story
    story = pyoscx.Story('mystory')
    story.add_act(act)

    ## create the storyboard
    sb = pyoscx.StoryBoard(init,pyoscx.ValueTrigger('stop_simulation',0,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(ttc_at_speed*2+acceleration_time,pyoscx.Rule.greaterThan),'stop'))
    sb.add_story(story)

    ## create and return the scenario
    sce = pyoscx.Scenario('CCRs v: ' +str(ego_speedvalue) + ', offset: ' + str(offset),'Mandolin',paramdec,entities=entities,storyboard = sb,roadnetwork=road,catalog=catalog)
    return sce

if __name__ == '__main__':
    all_egospeeds = [x for x in range(10,85,5)]

    all_offsets = [-50, -25, 0, 25, 50]
    sce = CCRs(all_egospeeds[14],all_offsets[1])
    # pyoscx.esminiRunner(sce)
