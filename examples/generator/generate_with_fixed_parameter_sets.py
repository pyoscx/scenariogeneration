"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.
  
    Example of creating OpenSCENARIO and OpenDRIVE files with a fixed set of dictionaries that will generate the scenarios and roads

    Example usage: when very precise permutations of a scenario is wanted

    Will generate 2 different scenarios and roads.
"""

from scenariogeneration import xodr
from scenariogeneration import xosc, prettyprint
from scenariogeneration import ScenarioGenerator


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
        self.naming = "parameter"

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
    s.print_permutations()
    s.generate("my_scenarios")
