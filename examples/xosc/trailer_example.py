"""
scenariogeneration
https://github.com/pyoscx/scenariogeneration

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2022 The scenariogeneration Authors.

  Simple example showing how one vehicle connects to a trailer

  Some features used:
  - HitchCoupler

  - TrailerConnectAction

  - TrailerDisconnectAction

  - StoryboardElementStateCondition

"""

import os

from scenariogeneration import ScenarioGenerator, prettyprint, xosc


class Scenario(ScenarioGenerator):
    def __init__(self):
        super().__init__()
        self.open_scenario_version = 2

    def scenario(self, **kwargs):
        ### create catalogs
        catalog = xosc.Catalog()

        ### create road
        road = xosc.RoadNetwork(roadfile="../xodr/straight_500m.xodr")

        ### create entities

        trailername = "trailer"

        bb = xosc.BoundingBox(2, 5, 1.8, 1.0, 0, 0.9)
        fa = xosc.Axle(0.523598775598, 0.8, 1.68, 2.98, 0.4)
        ba = xosc.Axle(0.523598775598, 0.8, 1.68, 0, 0.4)
        white_veh = xosc.Vehicle(
            "car_white",
            xosc.VehicleCategory.car,
            bb,
            fa,
            ba,
            69,
            10,
            10,
            trailer_hitch=xosc.HitchCoupler(-1.5),
        )

        white_veh.add_property_file("../models/car_white.osgb")

        bb = xosc.BoundingBox(1.8, 3, 0.5, 0, 0, 0.8)

        trailer = xosc.Vehicle(
            "car_red",
            xosc.VehicleCategory.trailer,
            bb,
            None,
            ba,
            69,
            10,
            10,
            trailer_coupler=xosc.HitchCoupler(1.6),
        )

        trailer.add_property_file("../models/car_trailer.osgb")

        ## create entities

        egoname = "Ego"

        entities = xosc.Entities()
        entities.add_scenario_object(egoname, white_veh)
        entities.add_scenario_object(trailername, trailer)

        ### create init

        init = xosc.Init()

        egostart = xosc.TeleportAction(xosc.LanePosition(25, 0, -1, 1))

        targetstart = xosc.TeleportAction(xosc.LanePosition(15, 0, -1, 1))

        init.add_init_action(egoname, egostart)
        init.add_init_action(trailername, targetstart)

        ### create an event

        ego_maneuver = xosc.Maneuver("ego pick up trailer")
        ego_event = xosc.Event("reverse", xosc.Priority.override)
        ego_event.add_trigger(
            xosc.ValueTrigger(
                "start reverse",
                0.5,
                xosc.ConditionEdge.none,
                xosc.SimulationTimeCondition(0, xosc.Rule.greaterThan),
            )
        )
        ego_event.add_action(
            "reverse action",
            xosc.AbsoluteSpeedAction(
                -2,
                xosc.TransitionDynamics(
                    xosc.DynamicsShapes.linear,
                    xosc.DynamicsDimension.time,
                    0.5,
                ),
            ),
        )

        ego_stop = xosc.Event("stop", xosc.Priority.override)
        ego_stop.add_trigger(
            xosc.EntityTrigger(
                "ego should stop",
                0,
                xosc.ConditionEdge.none,
                xosc.RelativeDistanceCondition(
                    0.05,
                    xosc.Rule.lessOrEqual,
                    xosc.RelativeDistanceType.longitudinal,
                    trailername,
                    alongroute=False,
                ),
                egoname,
            )
        )
        ego_stop.add_action(
            "stop action",
            xosc.AbsoluteSpeedAction(
                0,
                xosc.TransitionDynamics(
                    xosc.DynamicsShapes.linear,
                    xosc.DynamicsDimension.time,
                    0.1,
                ),
            ),
        )

        ego_hitch = xosc.Event("connect", xosc.Priority.override)
        ego_hitch.add_trigger(
            xosc.EntityTrigger(
                "stand still",
                0,
                xosc.ConditionEdge.none,
                xosc.StandStillCondition(1),
                egoname,
            )
        )
        ego_hitch.add_action(
            "connect trailer", xosc.ConnectTrailerAction(trailername)
        )

        ego_drive = xosc.Event("start driving", xosc.Priority.override)
        ego_drive.add_trigger(
            xosc.ValueTrigger(
                "start driving condition",
                1,
                xosc.ConditionEdge.none,
                xosc.StoryboardElementStateCondition(
                    xosc.StoryboardElementType.event,
                    "connect",
                    xosc.StoryboardElementState.completeState,
                ),
            )
        )
        ego_drive.add_action(
            "drive action action",
            xosc.AbsoluteSpeedAction(
                10,
                xosc.TransitionDynamics(
                    xosc.DynamicsShapes.cubic, xosc.DynamicsDimension.time, 5
                ),
            ),
        )

        ego_detach = xosc.Event("disconnect", xosc.Priority.parallel)
        ego_detach.add_trigger(
            xosc.ValueTrigger(
                "disconnect trailer",
                0,
                xosc.ConditionEdge.none,
                xosc.SimulationTimeCondition(8, xosc.Rule.greaterThan),
            )
        )
        ego_detach.add_action(
            "disconnect trailer", xosc.DisconnectTrailerAction()
        )

        ego_maneuver.add_event(ego_event)
        ego_maneuver.add_event(ego_stop)
        ego_maneuver.add_event(ego_hitch)
        ego_maneuver.add_event(ego_drive)
        ego_maneuver.add_event(ego_detach)

        ## create the storyboard
        sb = xosc.StoryBoard(init)
        sb.add_maneuver(ego_maneuver, egoname)
        paramdec = xosc.ParameterDeclarations()
        ## create the scenario
        sce = xosc.Scenario(
            "adapt_speed_example",
            "Mandolin",
            paramdec,
            entities=entities,
            storyboard=sb,
            roadnetwork=road,
            catalog=catalog,
            osc_minor_version=3,
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

    # esmini(sce, os.path.join("esmini"))
