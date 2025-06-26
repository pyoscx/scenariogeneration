"""
scenariogeneration
https://github.com/pyoscx/scenariogeneration

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2022 The scenariogeneration Authors.

  Fundamental example how to build up a road from scratch, but also with objects.

  This example should be seen as a developer example how roads are built up from the very basic classes in OpenDRIVE
  create_road will take care of this and much more, so a user is recommended to use that generator instead.

  Some features used:

  - Object

  - PlanView

  - Lane

  - Lanes

  - LaneSection

  - RoadMark

  - Road


"""

import os

import numpy as np

from scenariogeneration import ScenarioGenerator, prettyprint, xodr


class Scenario(ScenarioGenerator):
    def __init__(self):
        super().__init__()

    def road(self, **kwargs):
        ## EXAMPLE 1
        ## Multiple geometries in one only road. Additionally adding objects.

        ##1. Create the planview
        planview = xodr.PlanView()

        ##2. Create some geometries and add them to the planview
        line1 = xodr.Line(100)
        arc1 = xodr.Arc(0.05, angle=np.pi / 2)
        line2 = xodr.Line(100)
        cloth1 = xodr.Spiral(0.05, -0.1, 30)
        line3 = xodr.Line(100)

        planview.add_geometry(line1)
        planview.add_geometry(arc1)
        planview.add_geometry(line2)
        planview.add_geometry(cloth1)
        planview.add_geometry(line3)

        ##3. Create a solid roadmark
        rm = xodr.RoadMark(xodr.RoadMarkType.solid, 0.2)

        ##4. Create centerlane
        centerlane = xodr.Lane(a=2)
        centerlane.add_roadmark(rm)

        ##5. Create lane section form the centerlane
        lanesec = xodr.LaneSection(0, centerlane)

        ##6. Create left and right lanes
        lane2 = xodr.Lane(a=3)
        lane2.add_roadmark(rm)
        lane3 = xodr.Lane(a=3)
        lane3.add_roadmark(rm)

        ##7. Add lanes to lane section
        lanesec.add_left_lane(lane2)
        lanesec.add_right_lane(lane3)

        ##8. Add lane section to Lanes
        lanes = xodr.Lanes()
        lanes.add_lanesection(lanesec)

        ##9. Create Road from Planview and Lanes
        road = xodr.Road(1, planview, lanes)

        ##10. Create the OpenDrive class (Master class)
        odr = xodr.OpenDrive("myroad")

        ##11. Finally add roads to Opendrive
        odr.add_road(road)

        ##12. Adjust initial positions of the roads looking at succ-pred logic
        odr.adjust_roads_and_lanes()

        ##13. After adjustment, repeating objects on side of the road can be added automatically
        guardrail = xodr.Object(
            0,
            0,
            height=0.3,
            zOffset=0.4,
            Type=xodr.ObjectType.barrier,
            name="guardRail",
        )
        road.add_object_roadside(guardrail, 0, 0, tOffset=0.8)

        delineator = xodr.Object(
            0,
            0,
            height=1,
            zOffset=0,
            Type=xodr.ObjectType.pole,
            name="delineator",
        )
        road.add_object_roadside(delineator, 50, sOffset=25, tOffset=0.85)

        ##14. Add some other objects at specific positions
        # single emergency callbox
        emergencyCallbox = xodr.Object(
            30, -6, Type=xodr.ObjectType.pole, name="emergencyCallBox"
        )
        road.add_object(emergencyCallbox)

        # repeating jersey barrier
        jerseyBarrier = xodr.Object(
            0,
            0,
            height=0.75,
            zOffset=0,
            Type=xodr.ObjectType.barrier,
            name="jerseyBarrier",
        )
        jerseyBarrier.repeat(repeatLength=25, repeatDistance=0, sStart=240)
        road.add_object(jerseyBarrier)

        return odr


if __name__ == "__main__":
    sce = Scenario()
    # Print the resulting xml
    prettyprint(sce.road().get_element())

    # write the OpenDRIVE file as xosc using current script name
    sce.generate(".")

    # uncomment the following lines to display the scenario using esmini
    # from scenariogeneration import esmini
    # esmini(sce,os.path.join('esmini'))
