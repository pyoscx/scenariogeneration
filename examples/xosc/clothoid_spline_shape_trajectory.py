"""
scenariogeneration
https://github.com/pyoscx/scenariogeneration

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2022 The scenariogeneration Authors.

  Simple example showing how to use a ClothoidSpline as a trajectory for a vehicle.

  Some features used:

  - ClothoidSplineSegment

  - ClothoidSpline

"""

from scenariogeneration.xosc.position import (
    ClothoidSplineSegment,
    ClothoidSpline,
)
from scenariogeneration import xosc, prettyprint, ScenarioGenerator


class Scenario(ScenarioGenerator):
    def __init__(self):
        super().__init__()
        self.open_scenario_version = 3

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

        ## loop to create cars, init and their reset actions

        egoname = "Ego"
        targetname = "Target"
        entities = xosc.Entities()
        act = xosc.Act("indef traffic")

        entities.add_scenario_object(
            egoname, xosc.CatalogReference("VehicleCatalog", "car_white")
        )
        entities.add_scenario_object(
            targetname, xosc.CatalogReference("VehicleCatalog", "car_yellow")
        )

        ### create init

        init = xosc.Init()

        init.add_init_action(
            egoname, xosc.TeleportAction(xosc.LanePosition(10, 0, -2, 0))
        )
        init.add_init_action(
            egoname,
            xosc.AbsoluteSpeedAction(
                20,
                xosc.TransitionDynamics(
                    xosc.DynamicsShapes.linear, xosc.DynamicsDimension.time, 1
                ),
            ),
        )

        init.add_init_action(
            targetname, xosc.TeleportAction(xosc.LanePosition(50, 0, -3, 0))
        )
        init.add_init_action(
            targetname,
            xosc.AbsoluteSpeedAction(
                10,
                xosc.TransitionDynamics(
                    xosc.DynamicsShapes.linear, xosc.DynamicsDimension.time, 1
                ),
            ),
        )

        ## create the clothoid segments
        segment1 = ClothoidSplineSegment(
            curvature_start=0.0, curvature_end=-0.08, length=10.0
        )

        # position = xosc.LanePosition(20,0, -3, 0)
        segment2 = ClothoidSplineSegment(
            curvature_start=-0.08,
            curvature_end=0.0,
            length=10.0,
            h_offset=0.01,
            time_start=5.0,
            # position_start=[position],
        )
        segments = [segment1, segment2]
        clothoid_spline = ClothoidSpline(segments=segments, time_end=10)
        trajectory = xosc.Trajectory("trajectory", False)
        trajectory.add_shape(clothoid_spline)
        trajact = xosc.FollowTrajectoryAction(
            trajectory,
            xosc.FollowingMode.position,
            xosc.ReferenceContext.relative,
            1,
            0,
        )
        event = xosc.Event("my_event", xosc.Priority.overwrite)
        event.add_action("newspeed", trajact)

        ## create the act
        man = xosc.Maneuver("my_maneuver")
        man.add_event(event)

        mangr = xosc.ManeuverGroup("mangroup")
        mangr.add_actor("$owner")
        mangr.add_maneuver(man)
        starttrigger = xosc.ValueTrigger(
            "starttrigger",
            0,
            xosc.ConditionEdge.rising,
            xosc.SimulationTimeCondition(0, xosc.Rule.greaterThan),
        )
        act = xosc.Act("my_act", starttrigger)
        act.add_maneuver_group(mangr)

        ## create the story
        storyparam = xosc.ParameterDeclarations()
        storyparam.add_parameter(
            xosc.Parameter("$owner", xosc.ParameterType.string, egoname)
        )
        story = xosc.Story("mystory", storyparam)
        story.add_act(act)

        ## create the storyboard
        sb = xosc.StoryBoard(init)
        sb.add_story(story)

        ## create the scenario
        sce = xosc.Scenario(
            "ClothoidSpline_trajectory_example",
            "ekelidar",
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
    # import os

    # esmini(sce, os.path.join("../esmini"))
