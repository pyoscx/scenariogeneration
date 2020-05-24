
import pytest


import pyoscx as OSC




def test_road():
    roadfile = 'Databases/SampleDatabase.xodr'
    road = OSC.RoadNetwork(roadfile)
    OSC.prettyprint(road.get_element())


def test_catalog():

    catalog = OSC.Catalog()
    catalog.add_catalog('VehicleCatalog','Catalogs/VehicleCatalogs')
    catalog.add_catalog('ControllerCatalog','Catalogs/ControllerCatalogs')
    OSC.prettyprint(catalog.get_element())


def test_scenario():
    catalog = OSC.Catalog()
    catalog.add_catalog('VehicleCatalog','Catalogs/VehicleCatalogs')
    catalog.add_catalog('ControllerCatalog','Catalogs/ControllerCatalogs')

    roadfile = 'Databases/SampleDatabase.xodr'
    road = OSC.RoadNetwork(roadfile)

    trigcond = OSC.TimeToCollisionCondition(10,'equalTo',True,freespace=False,position=OSC.WorldPosition())

    trigger = OSC.EntityTrigger('mytesttrigger',0.2,'rising',trigcond,'Target_1')

    event = OSC.Event('myfirstevent','overwrite')
    event.add_trigger(trigger)

    TD = OSC.TransitionDynamics('step','rate',1)

    lanechangeaction = OSC.AbsoluteLaneChangeAction(1,TD)
    OSC.prettyprint(lanechangeaction.get_element())

    speedaction = OSC.AbsoluteSpeedAction(50,TD)
    event.add_action('newspeed',speedaction)

    man = OSC.Maneuver('my maneuver')
    man.add_event(event)

    mangr = OSC.ManeuverGroup('mangroup')
    mangr.add_actor('Ego')
    mangr.add_maneuver(man)

    act = OSC.Act('my act',trigger)
    act.add_maneuver_group(mangr)

    story = OSC.Story('mystory')
    story.add_act(act)

    bb = OSC.BoundingBox(2,5,1.5,1.5,0,0.2)
    fa = OSC.Axel(2,2,2,1,1)
    ba = OSC.Axel(1,1,2,1,1)
    veh = OSC.Vehicle('mycar','vehicle',bb,fa,ba,150,10,10)

    entities = OSC.Entities()
    entities.add_scenario_object('Ego',veh)
    entities.add_scenario_object('Target_1',veh)

    init = OSC.Init()
    egospeed = OSC.AbsoluteSpeedAction(10,TD)


    init.add_init_action('Ego',egospeed)
    init.add_init_action('Ego',OSC.TeleportAction(OSC.WorldPosition(1,2,3,0,0,0)))
    init.add_init_action('Target_1',egospeed)
    init.add_init_action('Target_1',OSC.TeleportAction(OSC.WorldPosition(1,5,3,0,0,0)))

    sb = OSC.StoryBoard(init)
    sb.add_story(story)

    sce = OSC.Scenario('myscenario','Mandolin',OSC.ParameterDeclarations(),entities=entities,storyboard = sb,roadnetwork=road,catalog=catalog)
    OSC.prettyprint(sce.get_element())