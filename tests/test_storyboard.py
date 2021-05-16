import pytest


from scenariogeneration import xosc as OSC
from scenariogeneration import prettyprint

TD = OSC.TransitionDynamics(OSC.DynamicsShapes.step,OSC.DynamicsDimension.rate,1)
speedaction = OSC.AbsoluteSpeedAction(50,TD)
trigcond = OSC.TimeToCollisionCondition(10,OSC.Rule.equalTo,position=OSC.WorldPosition(),freespace=False,)

trigger = OSC.EntityTrigger('mytesttrigger',0.2,OSC.ConditionEdge.rising,trigcond,'Target_1')

def test_event():

    event = OSC.Event('myfirstevent',OSC.Priority.overwrite)
    event.add_trigger(trigger)

    event.add_action('newspeed',speedaction)

    event2 = OSC.Event('myfirstevent',OSC.Priority.overwrite)
    event2.add_trigger(trigger)
    event2.add_action('newspeed',speedaction)
    event3 = OSC.Event('myfirstevent',OSC.Priority.overwrite)
    event3.add_trigger(trigger)
    event3.add_action('newspeed',speedaction)
    event3.add_action('newspeed2',speedaction)
    assert event == event2
    assert event != event3

def test_maneuver():
    event = OSC.Event('myfirstevent',OSC.Priority.overwrite)
    event.add_trigger(trigger)
    event.add_action('newspeed',speedaction)
    man = OSC.Maneuver('my maneuver')
    man.add_event(event)
    prettyprint(man.get_element())
    man2 = OSC.Maneuver('my maneuver')
    man2.add_event(event)
    man3 = OSC.Maneuver('my maneuver')
    man3.add_event(event)
    man3.add_event(event)
    assert man == man2
    assert man != man3

def test_maneuvergroup():
    event = OSC.Event('myfirstevent',OSC.Priority.overwrite)
    event.add_trigger(trigger)
    event.add_action('newspeed',speedaction)
    man = OSC.Maneuver('my maneuver')
    man.add_event(event)
    prettyprint(man.get_element())

    mangr = OSC.ManeuverGroup('mangroup')
    mangr.add_actor('Ego')
    mangr.add_maneuver(man)
    prettyprint(mangr.get_element())

    mangr2 = OSC.ManeuverGroup('mangroup')
    mangr2.add_actor('Ego')
    mangr2.add_maneuver(man)


    mangr3 = OSC.ManeuverGroup('mangroup')
    mangr3.add_actor('2Ego')
    mangr3.add_maneuver(man)

    assert mangr == mangr2
    assert mangr != mangr3

def test_actandstory():
    event = OSC.Event('myfirstevent',OSC.Priority.overwrite)
    event.add_trigger(trigger)
    event.add_action('newspeed',speedaction)
    man = OSC.Maneuver('my maneuver')
    man.add_event(event)
    prettyprint(man.get_element())

    mangr = OSC.ManeuverGroup('mangroup')
    mangr.add_actor('Ego')
    mangr.add_maneuver(man)
    prettyprint(mangr.get_element())

    act = OSC.Act('my act',trigger)
    act.add_maneuver_group(mangr)
    prettyprint(act.get_element())

    act2 = OSC.Act('my act',trigger)
    act2.add_maneuver_group(mangr)

    act3 = OSC.Act('my act',trigger)
    act3.add_maneuver_group(mangr)
    act3.add_maneuver_group(mangr)
    assert act == act2
    assert act != act3

    story = OSC.Story('mystory')
    story.add_act(act)
    prettyprint(story.get_element())

    story2 = OSC.Story('mystory')
    story2.add_act(act)

    story3 = OSC.Story('mystory')
    story3.add_act(act3)

    assert story == story2
    assert story != story3

def test_init():




    init = OSC.Init()
    TD = OSC.TransitionDynamics(OSC.DynamicsShapes.step,OSC.DynamicsDimension.rate,1)
    egospeed = OSC.AbsoluteSpeedAction(10,TD)
    
    init.add_init_action('Ego',egospeed)
    init.add_init_action('Ego',OSC.TeleportAction(OSC.WorldPosition(1,2,3,0,0,0)))
    init.add_init_action('Target_1',egospeed)
    init.add_init_action('Target_1',OSC.TeleportAction(OSC.WorldPosition(1,5,3,0,0,0)))
    init.add_init_action('Target_2',egospeed)
    init.add_init_action('Target_2',OSC.TeleportAction(OSC.WorldPosition(10,2,3,0,0,0)))
    prettyprint(init.get_element())

    init2 = OSC.Init()
    init2.add_init_action('Ego',egospeed)
    init2.add_init_action('Ego',OSC.TeleportAction(OSC.WorldPosition(1,2,3,0,0,0)))
    init2.add_init_action('Target_1',egospeed)
    init2.add_init_action('Target_1',OSC.TeleportAction(OSC.WorldPosition(1,5,3,0,0,0)))
    init2.add_init_action('Target_2',egospeed)
    init2.add_init_action('Target_2',OSC.TeleportAction(OSC.WorldPosition(10,2,3,0,0,0)))

    init3 = OSC.Init()
    init3.add_init_action('Ego',OSC.TeleportAction(OSC.WorldPosition(1,2,3,0,0,0)))
    init3.add_init_action('Target_1',egospeed)
    init3.add_init_action('Target_1',OSC.TeleportAction(OSC.WorldPosition(1,5,3,0,0,0)))
    init3.add_init_action('Target_2',egospeed)
    init3.add_init_action('Target_2',OSC.TeleportAction(OSC.WorldPosition(10,2,3,0,0,0)))

    assert init == init2
    assert init != init3

def test_storyboard_story_input():
    init = OSC.Init()
    TD = OSC.TransitionDynamics(OSC.DynamicsShapes.step,OSC.DynamicsDimension.rate,1)
    egospeed = OSC.AbsoluteSpeedAction(10,TD)
      
    init.add_init_action('Ego',egospeed)
    init.add_init_action('Ego',OSC.TeleportAction(OSC.WorldPosition(1,2,3,0,0,0)))
    init.add_init_action('Target_1',egospeed)
    init.add_init_action('Target_1',OSC.TeleportAction(OSC.WorldPosition(1,5,3,0,0,0)))
    init.add_init_action('Target_2',egospeed)
    init.add_init_action('Target_2',OSC.TeleportAction(OSC.WorldPosition(10,2,3,0,0,0)))
    prettyprint(init.get_element())





    event = OSC.Event('myfirstevent',OSC.Priority.overwrite)
    event.add_trigger(trigger)
    event.add_action('newspeed',speedaction)
    man = OSC.Maneuver('my maneuver')
    man.add_event(event)
    prettyprint(man.get_element())

    mangr = OSC.ManeuverGroup('mangroup')
    mangr.add_actor('Ego')
    mangr.add_maneuver(man)
    prettyprint(mangr.get_element())


    act = OSC.Act('my act',trigger)
    act.add_maneuver_group(mangr)
    prettyprint(act.get_element())

    story = OSC.Story('mystory')
    story.add_act(act)
    prettyprint(story.get_element())

    sb = OSC.StoryBoard(init)
    sb.add_story(story)
    prettyprint(sb.get_element())
    sb2 = OSC.StoryBoard(init)
    sb2.add_story(story)
    sb3 = OSC.StoryBoard(init)
    sb3.add_story(story)
    sb3.add_story(story)

    assert sb == sb2
    assert sb != sb3

def test_storyboard_act_input():
    
    egoname = "Ego"
    targetname = "target"

    init = OSC.Init()
    step_time = OSC.TransitionDynamics(OSC.DynamicsShapes.step,OSC.DynamicsDimension.time,1)

    egospeed = OSC.AbsoluteSpeedAction(0,step_time)
    egostart = OSC.TeleportAction(OSC.LanePosition(25,0,-3,0))

    targetspeed = OSC.AbsoluteSpeedAction(0,step_time)
    targetstart = OSC.TeleportAction(OSC.LanePosition(15,0,-2,0))

    init.add_init_action(egoname,egospeed)
    init.add_init_action(egoname,egostart)
    init.add_init_action(targetname,targetspeed)
    init.add_init_action(targetname,targetstart)


    ### create an event

    # trigcond = OSC.TimeHeadwayCondition(targetname,0.1,OSC.Rule.greaterThan)

    # trigger = OSC.EntityTrigger('mytesttrigger',0.2,OSC.ConditionEdge.rising,trigcond,egoname)
    trigger = OSC.ValueTrigger('starttrigger',0,OSC.ConditionEdge.rising,OSC.SimulationTimeCondition(3,OSC.Rule.greaterThan))
    event = OSC.Event('myfirstevent',OSC.Priority.overwrite)
    event.add_trigger(trigger)

    # sin_time = OSC.TransitionDynamics(OSC.DynamicsShapes.linear,OSC.DynamicsDimension.time,3)
    action = OSC.LongitudinalDistanceAction(-4,egoname,max_deceleration=3,max_speed=50)
    event.add_action('newspeed',action)


    ## create the act, 
    man = OSC.Maneuver('my_maneuver')
    man.add_event(event)

    mangr = OSC.ManeuverGroup('mangroup')
    mangr.add_actor(targetname)
    mangr.add_maneuver(man)

    starttrigger = OSC.ValueTrigger('starttrigger',0,OSC.ConditionEdge.rising,OSC.SimulationTimeCondition(0,OSC.Rule.greaterThan))
    act = OSC.Act('my_act',starttrigger)
    act.add_maneuver_group(mangr)

    ## create the storyboard
    sb = OSC.StoryBoard(init)
    sb.add_act(act)


    prettyprint(sb.get_element())

    sb2 = OSC.StoryBoard(init)
    sb2.add_act(act)

    sb3 = OSC.StoryBoard(init)
    sb3.add_act(act)
    sb3.add_act(act)

    assert sb == sb2
    assert sb != sb3


def test_storyboard_mangr_input():
    
    egoname = "Ego"
    targetname = "target"

    init = OSC.Init()
    step_time = OSC.TransitionDynamics(OSC.DynamicsShapes.step,OSC.DynamicsDimension.time,1)

    egospeed = OSC.AbsoluteSpeedAction(0,step_time)
    egostart = OSC.TeleportAction(OSC.LanePosition(25,0,-3,0))

    targetspeed = OSC.AbsoluteSpeedAction(0,step_time)
    targetstart = OSC.TeleportAction(OSC.LanePosition(15,0,-2,0))

    init.add_init_action(egoname,egospeed)
    init.add_init_action(egoname,egostart)
    init.add_init_action(targetname,targetspeed)
    init.add_init_action(targetname,targetstart)


    ### create an event

    # trigcond = OSC.TimeHeadwayCondition(targetname,0.1,OSC.Rule.greaterThan)

    # trigger = OSC.EntityTrigger('mytesttrigger',0.2,OSC.ConditionEdge.rising,trigcond,egoname)
    trigger = OSC.ValueTrigger('starttrigger',0,OSC.ConditionEdge.rising,OSC.SimulationTimeCondition(3,OSC.Rule.greaterThan))
    event = OSC.Event('myfirstevent',OSC.Priority.overwrite)
    event.add_trigger(trigger)

    # sin_time = OSC.TransitionDynamics(OSC.DynamicsShapes.linear,OSC.DynamicsDimension.time,3)
    action = OSC.LongitudinalDistanceAction(-4,egoname,max_deceleration=3,max_speed=50)
    event.add_action('newspeed',action)


    ## create the ManeuverGroup, 
    man = OSC.Maneuver('my_maneuver')
    man.add_event(event)

    mangr = OSC.ManeuverGroup('mangroup')
    mangr.add_actor(targetname)
    mangr.add_maneuver(man)



    ## create the storyboard
    sb = OSC.StoryBoard(init)
    sb.add_maneuver_group(mangr)

    prettyprint(sb.get_element())
    
    sb2 = OSC.StoryBoard(init)
    sb2.add_maneuver_group(mangr)
    sb3 = OSC.StoryBoard(init)
    sb3.add_maneuver_group(mangr)
    sb3.add_maneuver_group(mangr)
    
    assert sb == sb2
    assert sb != sb3


def test_storyboard_man_input():
    
    egoname = "Ego"
    targetname = "target"

    init = OSC.Init()
    step_time = OSC.TransitionDynamics(OSC.DynamicsShapes.step,OSC.DynamicsDimension.time,1)

    egospeed = OSC.AbsoluteSpeedAction(0,step_time)
    egostart = OSC.TeleportAction(OSC.LanePosition(25,0,-3,0))

    targetspeed = OSC.AbsoluteSpeedAction(0,step_time)
    targetstart = OSC.TeleportAction(OSC.LanePosition(15,0,-2,0))

    init.add_init_action(egoname,egospeed)
    init.add_init_action(egoname,egostart)
    init.add_init_action(targetname,targetspeed)
    init.add_init_action(targetname,targetstart)


    ### create an event

    # trigcond = OSC.TimeHeadwayCondition(targetname,0.1,OSC.Rule.greaterThan)

    # trigger = OSC.EntityTrigger('mytesttrigger',0.2,OSC.ConditionEdge.rising,trigcond,egoname)
    trigger = OSC.ValueTrigger('starttrigger',0,OSC.ConditionEdge.rising,OSC.SimulationTimeCondition(3,OSC.Rule.greaterThan))
    event = OSC.Event('myfirstevent',OSC.Priority.overwrite)
    event.add_trigger(trigger)

    # sin_time = OSC.TransitionDynamics(OSC.DynamicsShapes.linear,OSC.DynamicsDimension.time,3)
    action = OSC.LongitudinalDistanceAction(-4,egoname,max_deceleration=3,max_speed=50)
    event.add_action('newspeed',action)


    ## create the maneuver, 
    man = OSC.Maneuver('my_maneuver')
    man.add_event(event)

    ## create the storyboard
    sb = OSC.StoryBoard(init)
    sb.add_maneuver(man,targetname)


    prettyprint(sb.get_element())

    sb2 = OSC.StoryBoard(init)
    sb2.add_maneuver(man,targetname)

    sb3 = OSC.StoryBoard(init)
    sb3.add_maneuver(man,targetname)
    sb3.add_maneuver(man,targetname)

    assert sb == sb2
    assert sb != sb3

def test_empty_storyboard():

    ## create the storyboard
    sb = OSC.StoryBoard()
   


    prettyprint(sb.get_element())