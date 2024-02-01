"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2022 The scenariogeneration Authors.

    Fundamental example how to build up a road merge with lane merge afterwards.

    This simple example could be handled with the LaneDef (as in highway_example_with_merge_and_split.py)

    This example should be seen as a way to create your own complex merge case that the LaneDef + create_road cannot handle

    Some features used:

    - create_road

    - lane_offset

    - LaneSection

    - Lanes

"""

from scenariogeneration import xodr, prettyprint, ScenarioGenerator
import os


class Scenario(ScenarioGenerator):
    def __init__(self):
        super().__init__()

    def road(self, **kwargs):
        # create some roads
        roads = [xodr.create_road(xodr.Line(100), id=0, left_lanes=0, right_lanes=2)]

        roads.append(
            xodr.create_road(xodr.Line(100), id=1, left_lanes=0, right_lanes=1)
        )

        # manually create the final road

        # create the planview and the geometry
        planview = xodr.PlanView()
        planview.add_geometry(xodr.Line(200))

        # create two different roadmarkings
        rm_solid = xodr.RoadMark(xodr.RoadMarkType.solid, 0.2)
        rm_dashed = xodr.RoadMark(xodr.RoadMarkType.broken, 0.2)

        # create a centerlane (same centerlane can be used since no linking is needed for this)
        centerlane = xodr.Lane(a=2)
        centerlane.add_roadmark(rm_solid)

        # create the first lanesection with three lanes
        lanesec1 = xodr.LaneSection(0, centerlane)
        lane1 = xodr.Lane(a=3)
        lane1.add_roadmark(rm_dashed)

        lane2 = xodr.Lane(a=3)
        lane2.add_roadmark(rm_dashed)

        lane3 = xodr.Lane(a=3)
        lane3.add_roadmark(rm_solid)

        lanesec1.add_right_lane(lane1)
        lanesec1.add_right_lane(lane2)
        lanesec1.add_right_lane(lane3)

        # create the second lanesection with one lane merging
        lanesec2 = xodr.LaneSection(70, centerlane)
        lane4 = xodr.Lane(a=3)
        lane4.add_roadmark(rm_dashed)

        lane5 = xodr.Lane(a=3)
        lane5.add_roadmark(rm_dashed)

        lane6 = xodr.Lane(a=3, b=-0.1)
        lane6.add_roadmark(rm_solid)

        lanesec2.add_right_lane(lane4)
        lanesec2.add_right_lane(lane5)
        lanesec2.add_right_lane(lane6)

        # create the last lanesection with one lane
        lanesec3 = xodr.LaneSection(100, centerlane)

        lane7 = xodr.Lane(a=3)
        lane7.add_roadmark(rm_dashed)

        lane8 = xodr.Lane(a=3)
        lane8.add_roadmark(rm_solid)

        lanesec3.add_right_lane(lane7)
        lanesec3.add_right_lane(lane8)

        # create the lane links
        lanelinker = xodr.LaneLinker()
        lanelinker.add_link(predlane=lane1, succlane=lane4)
        lanelinker.add_link(predlane=lane2, succlane=lane5)
        lanelinker.add_link(predlane=lane3, succlane=lane6)

        lanelinker.add_link(predlane=lane5, succlane=lane7)
        lanelinker.add_link(predlane=lane6, succlane=lane8)

        # create the lanes with the correct links
        lanes = xodr.Lanes()
        lanes.add_lanesection(lanesec1, lanelinker)
        lanes.add_lanesection(lanesec2, lanelinker)
        lanes.add_lanesection(lanesec3, lanelinker)

        # create the road
        roads.append(xodr.Road(2, planview, lanes))

        # create junction roads
        roads.append(
            xodr.create_road(
                xodr.Spiral(0.001, 0.02, 30),
                id=3,
                left_lanes=0,
                right_lanes=2,
                road_type=1,
            )
        )
        roads.append(
            xodr.create_road(
                xodr.Spiral(-0.001, -0.02, 30),
                id=4,
                left_lanes=0,
                right_lanes=1,
                road_type=1,
            )
        )

        # add some connections to non junction roads
        roads[0].add_successor(xodr.ElementType.junction, 1)
        roads[1].add_successor(xodr.ElementType.junction, 1)
        roads[2].add_predecessor(xodr.ElementType.junction, 1)

        # add connections to the first connecting road
        roads[3].add_predecessor(xodr.ElementType.road, 0, xodr.ContactPoint.end)
        roads[3].add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.start)

        # add connections to the second connecting road with an offset
        roads[4].add_predecessor(xodr.ElementType.road, 1, xodr.ContactPoint.end)
        roads[4].add_successor(
            xodr.ElementType.road, 2, xodr.ContactPoint.start, lane_offset=-2
        )

        junction = xodr.create_junction(roads[3:], 1, roads[:3])

        # create the opendrive
        odr = xodr.OpenDrive("myroad")
        for r in roads:
            odr.add_road(r)
        odr.adjust_roads_and_lanes()
        odr.add_junction(junction)

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
