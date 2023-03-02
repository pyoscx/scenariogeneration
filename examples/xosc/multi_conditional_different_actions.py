"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2022 The scenariogeneration Authors.

    An example showing how to setup a choise for one vehicle depending on what is happening around it, using multi conditions with different rules

    for different behaviour change speed_of_outer_car

    Some features used:
    - ConditionGroup

    - TimeToCollisionCondition

    - TimeHeadwayCondition

    - AbsoluteSpeedAction

    - AbsoluteLaneChangeAction

    - Rule

"""
# change this to have different Ego behaviors (use 20 or 30)
speed_of_outer_car = 20

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
        speedyname = "speedy_gonzales"
        targetname = "Target"
        entities = xosc.Entities()
        entities.add_scenario_object(
            egoname, xosc.CatalogReference("VehicleCatalog", "car_white")
        )
        entities.add_scenario_object(
            speedyname, xosc.CatalogReference("VehicleCatalog", "car_blue")
        )
        entities.add_scenario_object(
            targetname, xosc.CatalogReference("VehicleCatalog", "car_yellow")
        )

        ### create init

        init = xosc.Init()

        init.add_init_action(
            egoname, xosc.TeleportAction(xosc.LanePosition(50, 0, -2, 0))
        )
        init.add_init_action(
            egoname,
            xosc.AbsoluteSpeedAction(
                15,
                xosc.TransitionDynamics(
                    xosc.DynamicsShapes.step, xosc.DynamicsDimension.time, 1
                ),
            ),
        )

        # change speed of this to have different outcome
        init.add_init_action(
            speedyname, xosc.TeleportAction(xosc.LanePosition(10, 0, -3, 0))
        )
        init.add_init_action(
            speedyname,
            xosc.AbsoluteSpeedAction(
                speed_of_outer_car,
                xosc.TransitionDynamics(
                    xosc.DynamicsShapes.step, xosc.DynamicsDimension.time, 1
                ),
            ),
        )

        init.add_init_action(
            targetname, xosc.TeleportAction(xosc.LanePosition(100, 0, -2, 0))
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

        ### create the "optional" slowdown event

        slowdown_event = xosc.Event("speedchange", xosc.Priority.overwrite)
        slowdown_event.add_action(
            "speedaction",
            xosc.AbsoluteSpeedAction(
                9,
                xosc.TransitionDynamics(
                    xosc.DynamicsShapes.sinusoidal, xosc.DynamicsDimension.time, 1
                ),
            ),
        )

        # create two trigger conditions
        ttc_cond = xosc.TimeToCollisionCondition(
            3, xosc.Rule.lessThan, entity=targetname
        )
        headway_cond = xosc.TimeHeadwayCondition(speedyname, 1, xosc.Rule.lessThan)

        headway_trigger = xosc.EntityTrigger(
            "trigger", 0, xosc.ConditionEdge.none, headway_cond, egoname
        )

        collision_trigger = xosc.EntityTrigger(
            "trigger", 0, xosc.ConditionEdge.none, ttc_cond, egoname
        )

        # create the "and" logic
        sc_group = xosc.ConditionGroup()
        sc_group.add_condition(collision_trigger)
        sc_group.add_condition(headway_trigger)

        slowdown_event.add_trigger(sc_group)

        # create the optional lanechange event
        lane_change_event = xosc.Event("lanechange", xosc.Priority.overwrite)

        lane_change_event.add_action(
            "lanechangeaction",
            xosc.AbsoluteLaneChangeAction(
                -3,
                xosc.TransitionDynamics(
                    xosc.DynamicsShapes.sinusoidal, xosc.DynamicsDimension.time, 3
                ),
            ),
        )

        # create two separate condition groups
        headway_cond_2 = xosc.TimeHeadwayCondition(speedyname, 1, xosc.Rule.greaterThan)
        headway_trigger_2 = xosc.EntityTrigger(
            "trigger", 0, xosc.ConditionEdge.none, headway_cond_2, egoname
        )

        ttc_cond_2 = xosc.TimeToCollisionCondition(
            3, xosc.Rule.lessThan, entity=targetname
        )
        collision_trigger_2 = xosc.EntityTrigger(
            "trigger", 0, xosc.ConditionEdge.none, ttc_cond_2, egoname
        )

        lc_group = xosc.ConditionGroup()
        lc_group.add_condition(headway_trigger_2)
        lc_group.add_condition(collision_trigger_2)

        lane_change_event.add_trigger(lc_group)

        ## create the storyboard
        man = xosc.Maneuver("slow down maneuver")

        man.add_event(slowdown_event)
        man.add_event(lane_change_event)

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
