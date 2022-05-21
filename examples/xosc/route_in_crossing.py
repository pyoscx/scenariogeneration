"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.
  
    Simple example showing how to pick a route in a junction

    Some features used:

    - Route

    - AssignRouteAction

    - LanePosition
"""
import os
from scenariogeneration import xosc, prettyprint

### create catalogs
catalog = xosc.Catalog()
catalog.add_catalog("VehicleCatalog", "../xosc/Catalogs/Vehicles")


### create road
road = xosc.RoadNetwork(
    roadfile="../xodr/fabriksgatan.xodr", scenegraph="../models/fabriksgatan.osgb"
)

### create parameters
paramdec = xosc.ParameterDeclarations()

## create entities

egoname = "Ego"
targetname = "Target"

entities = xosc.Entities()
entities.add_scenario_object(
    egoname, xosc.CatalogReference("VehicleCatalog", "car_red")
)

### create init

init = xosc.Init()

init.add_init_action(egoname, xosc.TeleportAction(xosc.LanePosition(50, 0, 1, 0)))
init.add_init_action(
    egoname,
    xosc.AbsoluteSpeedAction(
        10,
        xosc.TransitionDynamics(
            xosc.DynamicsShapes.step, xosc.DynamicsDimension.time, 1
        ),
    ),
)

# create a router

ego_route = xosc.Route("ego_route")
ego_route.add_waypoint(xosc.LanePosition(30, 0, 1, 0), xosc.RouteStrategy.fastest)
ego_route.add_waypoint(xosc.LanePosition(10, 0, -1, 1), xosc.RouteStrategy.fastest)


# create action
ego_action = xosc.AssignRouteAction(ego_route)


ego_event = xosc.Event("ego_event", xosc.Priority.overwrite)
ego_event.add_action("ego_route", ego_action)
ego_event.add_trigger(
    xosc.ValueTrigger(
        "target_start",
        0,
        xosc.ConditionEdge.none,
        xosc.SimulationTimeCondition(1, xosc.Rule.greaterThan),
    )
)


## create the storyboard
ego_man = xosc.Maneuver("ego_man")
ego_man.add_event(ego_event)

sb = xosc.StoryBoard(
    init,
    xosc.ValueTrigger(
        "stop_simulation",
        0,
        xosc.ConditionEdge.rising,
        xosc.SimulationTimeCondition(10, xosc.Rule.greaterThan),
        "stop",
    ),
)
sb.add_maneuver(ego_man, egoname)

## create the scenario
sce = xosc.Scenario(
    "adaptspeed_example",
    "User",
    paramdec,
    entities=entities,
    storyboard=sb,
    roadnetwork=road,
    catalog=catalog,
)

# Print the resulting xml
prettyprint(sce.get_element())

# write the OpenSCENARIO file as xosc using current script name
sce.write_xml(os.path.basename(__file__).replace(".py", ".xosc"))

# uncomment the following lines to display the scenario using esmini
# from scenariogeneration import esmini
# esmini(sce,os.path.join('esmini'))
