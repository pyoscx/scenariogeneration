"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.
  
    Example showing how one vehicle triggers based on the acceleration of another vehicle, then changes its speed.

    Some features used:

    - ParameterValueDistribution

    - Stocastic

    - NormalDistribution

    - Histogram

"""
import os
from scenariogeneration import xosc, prettyprint

# some names used in both scenario and
scenario_filename = "base_scenario.xosc"
ego_param_name = "$egospeed"
target_param_name = "$targetspeed"

### create a simple parametrized scenario

## create catalogs
catalog = xosc.Catalog()
catalog.add_catalog("VehicleCatalog", "../xosc/Catalogs/Vehicles")

## create road
road = xosc.RoadNetwork(roadfile="../xodr/e6mini.xodr")

## create parameters
paramdec = xosc.ParameterDeclarations()
paramdec.add_parameter(xosc.Parameter(ego_param_name, xosc.ParameterType.double, "10"))
paramdec.add_parameter(
    xosc.Parameter(target_param_name, xosc.ParameterType.double, "10")
)

## create entities

egoname = "Ego"
redname = "Target1"

entities = xosc.Entities()
entities.add_scenario_object(
    egoname, xosc.CatalogReference("VehicleCatalog", "car_white")
)
entities.add_scenario_object(
    redname, xosc.CatalogReference("VehicleCatalog", "car_red")
)

## create a parametrized init
init = xosc.Init()
step_time = xosc.TransitionDynamics(
    xosc.DynamicsShapes.step, xosc.DynamicsDimension.time, 1
)

init.add_init_action(egoname, xosc.AbsoluteSpeedAction(ego_param_name, step_time))
init.add_init_action(egoname, xosc.TeleportAction(xosc.LanePosition(25, 0, -3, 0)))
init.add_init_action(redname, xosc.AbsoluteSpeedAction(target_param_name, step_time))
init.add_init_action(redname, xosc.TeleportAction(xosc.LanePosition(15, 0, -2, 0)))

## create storyboard
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

## create the scenario file
sce = xosc.Scenario(
    "Parameter_example",
    "Mandolin",
    paramdec,
    entities=entities,
    storyboard=sb,
    roadnetwork=road,
    catalog=catalog,
)

## write and print the scenario
sce.write_xml(scenario_filename)

prettyprint(sce.get_element())

### create the paramtrization

## create a stocastic distribution with 100 runs
stoc = xosc.Stochastic(50, 1.234)

## add a Normal distribution for the ego
nd = xosc.NormalDistribution(25, 1)
stoc.add_distribution(ego_param_name, nd)

## add a histogram for the target
hg = xosc.Histogram()
hg.add_bin(0.3, xosc.Range(15, 25))
hg.add_bin(0.7, xosc.Range(25, 35))
stoc.add_distribution(target_param_name, hg)

## create the ParameterValueDistribution
pvd = xosc.ParameterValueDistribution(
    "my_parametrization", "Mandolin", scenario_filename, stoc
)

## Print the resulting xml
prettyprint(pvd.get_element())

## write the OpenSCENARIO file as xosc using current script name
pvd.write_xml(os.path.basename(__file__).replace(".py", ".xosc"))
