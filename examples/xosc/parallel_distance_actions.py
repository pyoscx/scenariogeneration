"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2022 The scenariogeneration Authors.

    Simple example showing how one vehicle triggers two different actions based on different distance related triggers

    Some features used:

    - ReachPositionCondition

    - RelativeDistanceCondition

    - RelativeLaneChangeAction

    - AbsoluteSpeedAction
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
            roadfile="../xodr/e6mini.xodr", scenegraph="../models/e6mini.osgb"
        )

        ### create parameters
        paramdec = xosc.ParameterDeclarations()

        ## create entities

        egoname = "Ego"
        egoref = "Egofake"
        targetname = "Target"
        entities = xosc.Entities()
        entities.add_scenario_object(
            egoname, xosc.CatalogReference("VehicleCatalog", "car_white")
        )
        entities.add_scenario_object(
            targetname, xosc.CatalogReference("VehicleCatalog", "car_yellow")
        )

        ### create init

        init = xosc.Init()

        init.add_init_action(
            egoname, xosc.TeleportAction(xosc.LanePosition(10, 0, -4, 0))
        )
        init.add_init_action(
            egoname,
            xosc.AbsoluteSpeedAction(
                20,
                xosc.TransitionDynamics(
                    xosc.DynamicsShapes.step, xosc.DynamicsDimension.time, 1
                ),
            ),
        )

        init.add_init_action(
            targetname, xosc.TeleportAction(xosc.LanePosition(50, 0, -2, 0))
        )
        init.add_init_action(
            targetname,
            xosc.AbsoluteSpeedAction(
                10,
                xosc.TransitionDynamics(
                    xosc.DynamicsShapes.step, xosc.DynamicsDimension.time, 1
                ),
            ),
        )

        ## do lanechange
        lc_cond = xosc.ReachPositionCondition(xosc.LanePosition(40, 0, -4, 0), 1)
        lc_event = xosc.Event("lanechange", xosc.Priority.parallel)
        lc_event.add_action(
            "lanechangeaction",
            xosc.RelativeLaneChangeAction(
                -1,
                targetname,
                xosc.TransitionDynamics(
                    xosc.DynamicsShapes.sinusoidal, xosc.DynamicsDimension.time, 3
                ),
            ),
        )
        lc_event.add_trigger(
            xosc.EntityTrigger(
                "lanechangetrigger", 0, xosc.ConditionEdge.none, lc_cond, egoname
            )
        )

        event = xosc.Event("speedchange", xosc.Priority.parallel)
        event.add_action(
            "speedaction",
            xosc.AbsoluteSpeedAction(
                10,
                xosc.TransitionDynamics(
                    xosc.DynamicsShapes.linear, xosc.DynamicsDimension.time, 3
                ),
            ),
        )
        trig_cond = xosc.RelativeDistanceCondition(
            5, xosc.Rule.lessThan, xosc.RelativeDistanceType.lateral, targetname
        )
        event.add_trigger(
            xosc.EntityTrigger(
                "trigger", 0, xosc.ConditionEdge.none, trig_cond, egoname
            )
        )

        man = xosc.Maneuver("mymaneuver")
        man.add_event(lc_event)
        man.add_event(event)

        ## create the storyboard
        sb = xosc.StoryBoard(
            init,
            xosc.ValueTrigger(
                "stop_simulation",
                0,
                xosc.ConditionEdge.rising,
                xosc.SimulationTimeCondition(20, xosc.Rule.greaterThan),
                "stop",
            ),
        )

        sb.add_maneuver(man, egoname)
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
