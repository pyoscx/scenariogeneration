import pytest


import pyoscx as OSC


TD = OSC.TransitionDynamics('step',0,'rate',1)

speedaction = OSC.SpeedAction(TD)
speedaction.set_absolute_target_speed(50)
trigcond = OSC.TimeToCollisionCondition(10,'equalTo',position=OSC.WorldPosition(),freespace=False,)

trigger = OSC.EntityTrigger('mytesttrigger',0.2,'rising',trigcond,'Target_1')

def test_event():

    event = OSC.Event('myfirstevent','overwrite')
    event.add_trigger(trigger)

    event.add_action('newspeed',speedaction)


def test_maneuver():
    event = OSC.Event('myfirstevent','overwrite')
    event.add_trigger(trigger)
    event.add_action('newspeed',speedaction)
    man = OSC.Maneuver('my maneuver')
    man.add_event(event)
    OSC.prettyprint(man.get_element())


def test_maneuvergroup():
    event = OSC.Event('myfirstevent','overwrite')
    event.add_trigger(trigger)
    event.add_action('newspeed',speedaction)
    man = OSC.Maneuver('my maneuver')
    man.add_event(event)
    OSC.prettyprint(man.get_element())

    mangr = OSC.ManeuverGroup('mangroup')
    mangr.add_actor('Ego')
    mangr.add_maneuver(man)
    OSC.prettyprint(mangr.get_element())


def test_actandstory():
    event = OSC.Event('myfirstevent','overwrite')
    event.add_trigger(trigger)
    event.add_action('newspeed',speedaction)
    man = OSC.Maneuver('my maneuver')
    man.add_event(event)
    OSC.prettyprint(man.get_element())

    mangr = OSC.ManeuverGroup('mangroup')
    mangr.add_actor('Ego')
    mangr.add_maneuver(man)
    OSC.prettyprint(mangr.get_element())

    act = OSC.Act('my act',trigger)
    act.add_maneuver_group(mangr)
    OSC.prettyprint(act.get_element())

    story = OSC.Story('mystory')
    story.add_act(act)
    OSC.prettyprint(story.get_element())

def test_init():




    init = OSC.Init()
    TD = OSC.TransitionDynamics('step',0,'time',0)
    egospeed = OSC.SpeedAction(TD)
    egospeed.set_absolute_target_speed(10)
    init.add_init_action('Ego',egospeed)
    init.add_init_action('Ego',OSC.TeleportAction(OSC.WorldPosition(1,2,3,0,0,0)))
    init.add_init_action('Target_1',egospeed)
    init.add_init_action('Target_1',OSC.TeleportAction(OSC.WorldPosition(1,5,3,0,0,0)))
    init.add_init_action('Target_2',egospeed)
    init.add_init_action('Target_2',OSC.TeleportAction(OSC.WorldPosition(10,2,3,0,0,0)))
    OSC.prettyprint(init.get_element())

def test_storyboard():
    init = OSC.Init()
    TD = OSC.TransitionDynamics('step',0,'time',0)
    egospeed = OSC.SpeedAction(TD)
    egospeed.set_absolute_target_speed(10)  
    init.add_init_action('Ego',egospeed)
    init.add_init_action('Ego',OSC.TeleportAction(OSC.WorldPosition(1,2,3,0,0,0)))
    init.add_init_action('Target_1',egospeed)
    init.add_init_action('Target_1',OSC.TeleportAction(OSC.WorldPosition(1,5,3,0,0,0)))
    init.add_init_action('Target_2',egospeed)
    init.add_init_action('Target_2',OSC.TeleportAction(OSC.WorldPosition(10,2,3,0,0,0)))
    OSC.prettyprint(init.get_element())





    event = OSC.Event('myfirstevent','overwrite')
    event.add_trigger(trigger)
    event.add_action('newspeed',speedaction)
    man = OSC.Maneuver('my maneuver')
    man.add_event(event)
    OSC.prettyprint(man.get_element())

    mangr = OSC.ManeuverGroup('mangroup')
    mangr.add_actor('Ego')
    mangr.add_maneuver(man)
    OSC.prettyprint(mangr.get_element())


    act = OSC.Act('my act',trigger)
    act.add_maneuver_group(mangr)
    OSC.prettyprint(act.get_element())

    story = OSC.Story('mystory')
    story.add_act(act)
    OSC.prettyprint(story.get_element())

    sb = OSC.StoryBoard(init)
    sb.add_story(story)
    OSC.prettyprint(sb.get_element())
