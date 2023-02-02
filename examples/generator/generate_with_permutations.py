"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2022 The scenariogeneration Authors.

    Example of creating OpenSCENARIO and OpenDRIVE files with parameter sweep type of input

    Example usage: When a parameter sweep is wanted with minimal input
    Using the generate_all_roads feature which will only generate unique roads

    Will generate 12 different scenarios and 4 different roads.
"""

from scenariogeneration import xodr
from scenariogeneration import xosc, prettyprint
from scenariogeneration import ScenarioGenerator


class Scenario(ScenarioGenerator):
    def __init__(self):
        ScenarioGenerator.__init__(self)

        self.parameters["road_curvature"] = [0.001, 0.002, 0.003, 0.004]
        self.parameters["speed"] = [10, 20, 30]
        self.naming = "numerical"

        # set so no duplicate roads are created
        self.generate_all_roads = False
        self.number_of_parallel_writings = 2

    def road(self, **kwargs):
        road = xodr.create_road(
            [
                xodr.Spiral(0.0000000001, kwargs["road_curvature"], 100),
                xodr.Arc(kwargs["road_curvature"], 50),
                xodr.Spiral(kwargs["road_curvature"], 0.0000000001, 100),
                xodr.Line(100),
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
            egoname, xosc.TeleportAction(xosc.LanePosition(50, 0, -2, 0))
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

        event = xosc.Event("my event", xosc.Priority.overwrite)
        event.add_action(
            "lane change",
            xosc.AbsoluteLaneChangeAction(
                -1,
                xosc.TransitionDynamics(
                    xosc.DynamicsShapes.sinusoidal, xosc.DynamicsDimension.time, 4
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
            "Mandolin",
            xosc.ParameterDeclarations(),
            entities,
            sb,
            road,
            catalog,
        )

        return sce


if __name__ == "__main__":
    s = Scenario()
    # s.print_permutations()
    files = s.generate("my_scenarios")
    # print(files)
