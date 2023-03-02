"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2022 The scenariogeneration Authors.

    Example showing how to create "repeating traffic" if a car goes to the end of the road

    Some features used:

        - multiple execusions

        - EndOfRoadCondition

        - Teleport

        - LanePosition

"""
import os
from scenariogeneration import xosc, prettyprint, ScenarioGenerator


class Scenario(ScenarioGenerator):
    def __init__(self):
        super().__init__()
        self.open_scenario_version = 2

    def scenario(self, **kwargs):
        ### create catalogs
        catalog = xosc.Catalog()
        catalog.add_catalog("VehicleCatalog", "../xosc/Catalogs/Vehicles")

        ### create road
        road = xosc.RoadNetwork(
            roadfile="../xodr/straight_500m.xodr",
            scenegraph="../models/straight_500m.osgb",
        )

        ### create parameters
        paramdec = xosc.ParameterDeclarations()

        ## loop to create cars, init and their reset actions

        egoname = "Ego"

        targetname = "Target"
        entities = xosc.Entities()
        init = xosc.Init()
        act = xosc.Act("indef traffic")

        for i in range(20):
            entities.add_scenario_object(
                targetname + str(i),
                xosc.CatalogReference("VehicleCatalog", "car_yellow"),
            )

            init.add_init_action(
                targetname + str(i),
                xosc.TeleportAction(xosc.LanePosition(100 + i * 20, 0, -1, 1)),
            )
            init.add_init_action(
                targetname + str(i),
                xosc.AbsoluteSpeedAction(
                    60,
                    xosc.TransitionDynamics(
                        xosc.DynamicsShapes.step, xosc.DynamicsDimension.time, 1
                    ),
                ),
            )

            event = xosc.Event("speedchange", xosc.Priority.overwrite, maxexecution=10)
            event.add_action(
                "restart", xosc.TeleportAction(xosc.LanePosition(0, 0, -1, 1))
            )

            trig_cond = xosc.EndOfRoadCondition(0)

            event.add_trigger(
                xosc.EntityTrigger(
                    "trigger",
                    0,
                    xosc.ConditionEdge.rising,
                    trig_cond,
                    targetname + str(i),
                )
            )

            man = xosc.Maneuver("mymaneuver")
            man.add_event(event)

            mangr = xosc.ManeuverGroup("mangr", maxexecution=3)
            mangr.add_maneuver(man)
            mangr.add_actor(targetname + str(i))
            act.add_maneuver_group(mangr)

        ## create the storyboard
        sb = xosc.StoryBoard(
            init,
            xosc.ValueTrigger(
                "stop_simulation",
                0,
                xosc.ConditionEdge.rising,
                xosc.SimulationTimeCondition(100, xosc.Rule.greaterThan),
                "stop",
            ),
        )

        sb.add_act(act)
        ## create the scenario
        sce = xosc.Scenario(
            "adaptspeed_example",
            "User",
            paramdec,
            entities=entities,
            storyboard=sb,
            roadnetwork=road,
            catalog=catalog,
            osc_minor_version=self.open_scenario_version,
        )
        return sce


if __name__ == "__main__":
    sce = Scenario()
    # Print the resulting xml
    prettyprint(sce.scenario().get_element())

    # write the OpenSCENARIO file as xosc using current script name
    sce.generate(".")

    # uncomment the following lines to display the scenario using esmini
    # from scenariogeneration import esmini
    # esmini(sce,os.path.join('esmini'))
