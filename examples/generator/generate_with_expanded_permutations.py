"""
scenariogeneration
https://github.com/pyoscx/scenariogeneration

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2022 The scenariogeneration Authors.

  Example of creating OpenSCENARIO and OpenDRIVE files with a combination of fixed parameter sets and parameter permutations that will generate the scenarios and roads

  Example usage: when very precise permutations of a scenario is wanted with additional parameter sweeps

  This example demonstrates how expand_permutations works with fixed parameter sets.

  Given:
    parameters = [
        {'road_curvature': 0.001, 'speed': 10},
        {'road_curvature': 0.002, 'speed': 20}
    ]

    expand_permutations = [
        {'initial_distance': [40, 50, 60], 'line_length': [100, 200]}
    ]

  The result will be 12 scenarios (2 base scenarios × 3 distances × 2 lengths):

    | Scenario | road_curvature | speed | initial_distance | line_length |
    |----------|----------------|-------|------------------|-------------|
    | 1        | 0.001          | 10    | 40               | 100         |
    | 2        | 0.001          | 10    | 40               | 200         |
    | 3        | 0.001          | 10    | 50               | 100         |
    | 4        | 0.001          | 10    | 50               | 200         |
    | 5        | 0.001          | 10    | 60               | 100         |
    | 6        | 0.001          | 10    | 60               | 200         |
    | 7        | 0.002          | 20    | 40               | 100         |
    | 8        | 0.002          | 20    | 40               | 200         |
    | 9        | 0.002          | 20    | 50               | 100         |
    | 10       | 0.002          | 20    | 50               | 200         |
    | 11       | 0.002          | 20    | 60               | 100         |
    | 12       | 0.002          | 20    | 60               | 200         |

"""

from scenariogeneration import ScenarioGenerator, xodr, xosc


class Scenario(ScenarioGenerator):
    def __init__(self):
        ScenarioGenerator.__init__(self)
        self.parameters = []
        d1 = {}
        d1["road_curvature"] = 0.001
        d1["speed"] = 10

        d2 = {}
        d2["road_curvature"] = 0.002
        d2["speed"] = 20

        self.parameters.append(d1)
        self.parameters.append(d2)

        d3 = {}
        d3["initial_distance"] = [40, 50, 60]
        d3["line_length"] = [100, 200]
        self.expand_permutations.append(d3)

        self.naming = "parameter"

    def road(self, **kwargs):
        road = xodr.create_road(
            [
                xodr.Spiral(0.0000000001, kwargs["road_curvature"], 100),
                xodr.Arc(kwargs["road_curvature"], 50),
                xodr.Spiral(kwargs["road_curvature"], 0.0000000001, 100),
                xodr.Line(kwargs["line_length"]),
            ],
            id=0,
            left_lanes=2,
            right_lanes=2,
        )
        odr = xodr.OpenDrive("myroad")
        odr.add_road(road)
        odr.adjust_roads_and_lanes()
        return odr

    def scenario(self, **kwargs):
        road = xosc.RoadNetwork(self.road_file)
        egoname = "Ego"
        entities = xosc.Entities()
        entities.add_scenario_object(
            egoname, xosc.CatalogReference("VehicleCatalog", "car_white")
        )

        catalog = xosc.Catalog()
        catalog.add_catalog("VehicleCatalog", "../xosc/Catalogs/Vehicles")

        init = xosc.Init()

        init.add_init_action(
            egoname,
            xosc.TeleportAction(
                xosc.LanePosition(kwargs["initial_distance"], 0, -2, 0)
            ),
        )
        init.add_init_action(
            egoname,
            xosc.AbsoluteSpeedAction(
                kwargs["speed"],
                xosc.TransitionDynamics(
                    xosc.DynamicsShapes.step, xosc.DynamicsDimension.time, 1
                ),
            ),
        )

        event = xosc.Event("my event", xosc.Priority.override)
        event.add_action(
            "lane change",
            xosc.AbsoluteLaneChangeAction(
                -1,
                xosc.TransitionDynamics(
                    xosc.DynamicsShapes.sinusoidal,
                    xosc.DynamicsDimension.time,
                    4,
                ),
            ),
        )
        event.add_trigger(
            xosc.ValueTrigger(
                "start_trigger ",
                0,
                xosc.ConditionEdge.none,
                xosc.SimulationTimeCondition(4, xosc.Rule.greaterThan),
            )
        )

        man = xosc.Maneuver("maneuver")
        man.add_event(event)

        sb = xosc.StoryBoard(
            init,
            stoptrigger=xosc.ValueTrigger(
                "start_trigger ",
                0,
                xosc.ConditionEdge.none,
                xosc.SimulationTimeCondition(13, xosc.Rule.greaterThan),
                "stop",
            ),
        )
        sb.add_maneuver(man, egoname)
        sce = xosc.Scenario(
            "my scenario",
            "atingber",
            xosc.ParameterDeclarations(),
            entities,
            sb,
            road,
            catalog,
        )

        return sce


if __name__ == "__main__":
    s = Scenario()
    s.print_permutations()
    s.generate("my_scenarios")
