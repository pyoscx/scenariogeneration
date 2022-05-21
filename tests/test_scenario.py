"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.

"""
import pytest
import datetime as dt

from scenariogeneration import xosc as OSC
from scenariogeneration import prettyprint
from scenariogeneration.xosc.utils import TrafficSignalController


def test_road():
    controller = OSC.TrafficSignalController("controllerName", 11, "ReferenceID")
    roadfile = "Databases/SampleDatabase.xodr"
    road = OSC.RoadNetwork(roadfile)
    prettyprint(road.get_element(), None)
    road2 = OSC.RoadNetwork(roadfile)
    road3 = OSC.RoadNetwork(roadfile, "a")
    assert road == road2
    assert road != road3
    road.add_used_area_position(OSC.WorldPosition())
    with pytest.raises(OSC.NotEnoughInputArguments):
        road.get_element()
    road.add_used_area_position(OSC.WorldPosition(1, 1, 1))
    road.add_traffic_signal_controller(controller)
    prettyprint(road.get_element(), None)

    road4 = OSC.RoadNetwork.parse(road.get_element())
    prettyprint(road4.get_element(), None)
    assert road4 == road


def test_catalog():

    catalog = OSC.Catalog()
    catalog.add_catalog("VehicleCatalog", "Catalogs/VehicleCatalogs")
    catalog.add_catalog("ControllerCatalog", "Catalogs/ControllerCatalogs")
    prettyprint(catalog.get_element())

    catalog2 = OSC.Catalog()
    catalog2.add_catalog("VehicleCatalog", "Catalogs/VehicleCatalogs")
    catalog2.add_catalog("ControllerCatalog", "Catalogs/ControllerCatalogs")

    catalog3 = OSC.Catalog()
    catalog3.add_catalog("VehicleCatalog", "Catalogs/VehicleCatalogs")

    assert catalog == catalog2
    assert catalog != catalog3

    catalog4 = OSC.Catalog.parse(catalog.get_element())
    prettyprint(catalog4.get_element(), None)
    assert catalog == catalog4


def test_scenario():
    catalog = OSC.Catalog()
    catalog.add_catalog("VehicleCatalog", "Catalogs/VehicleCatalogs")
    catalog.add_catalog("ControllerCatalog", "Catalogs/ControllerCatalogs")

    roadfile = "Databases/SampleDatabase.xodr"
    road = OSC.RoadNetwork(roadfile)

    trigcond = OSC.TimeToCollisionCondition(
        10, OSC.Rule.equalTo, True, freespace=False, position=OSC.WorldPosition()
    )

    trigger = OSC.EntityTrigger(
        "mytesttrigger", 0.2, OSC.ConditionEdge.rising, trigcond, "Target_1"
    )

    event = OSC.Event("myfirstevent", OSC.Priority.overwrite)
    event.add_trigger(trigger)

    TD = OSC.TransitionDynamics(OSC.DynamicsShapes.step, OSC.DynamicsDimension.rate, 1)

    lanechangeaction = OSC.AbsoluteLaneChangeAction(1, TD)
    prettyprint(lanechangeaction.get_element())

    speedaction = OSC.AbsoluteSpeedAction(50, TD)
    event.add_action("newspeed", speedaction)

    man = OSC.Maneuver("my maneuver")
    man.add_event(event)

    mangr = OSC.ManeuverGroup("mangroup")
    mangr.add_actor("Ego")
    mangr.add_maneuver(man)

    act = OSC.Act("my act", trigger)
    act.add_maneuver_group(mangr)

    story = OSC.Story("mystory")
    story.add_act(act)

    bb = OSC.BoundingBox(2, 5, 1.5, 1.5, 0, 0.2)
    fa = OSC.Axle(2, 2, 2, 1, 1)
    ba = OSC.Axle(1, 1, 2, 1, 1)
    veh = OSC.Vehicle("mycar", OSC.VehicleCategory.car, bb, fa, ba, 150, 10, 10)

    entities = OSC.Entities()
    entities.add_scenario_object("Ego", veh)
    entities.add_scenario_object("Target_1", veh)

    init = OSC.Init()
    egospeed = OSC.AbsoluteSpeedAction(10, TD)

    init.add_init_action("Ego", egospeed)
    init.add_init_action("Ego", OSC.TeleportAction(OSC.WorldPosition(1, 2, 3, 0, 0, 0)))
    init.add_init_action("Target_1", egospeed)
    init.add_init_action(
        "Target_1", OSC.TeleportAction(OSC.WorldPosition(1, 5, 3, 0, 0, 0))
    )

    sb = OSC.StoryBoard(init)
    sb.add_story(story)

    sce = OSC.Scenario(
        "myscenario",
        "Mandolin",
        OSC.ParameterDeclarations(),
        entities=entities,
        storyboard=sb,
        roadnetwork=road,
        catalog=catalog,
    )
    prettyprint(sce.get_element(), None)
    sce2 = OSC.Scenario(
        "myscenario",
        "Mandolin",
        OSC.ParameterDeclarations(),
        entities=entities,
        storyboard=sb,
        roadnetwork=road,
        catalog=catalog,
        creation_date=dt.datetime.now(),
    )
    sce3 = OSC.Scenario(
        "2myscenario",
        "Mandolin",
        OSC.ParameterDeclarations(),
        entities=entities,
        storyboard=sb,
        roadnetwork=road,
        catalog=catalog,
    )

    assert sce == sce2
    assert sce != sce3

    sce4 = OSC.Scenario.parse(sce.get_element())
    prettyprint(sce4.get_element(), None)
    assert sce == sce4
