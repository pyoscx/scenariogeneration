"""
scenariogeneration
https://github.com/pyoscx/scenariogeneration

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2022 The scenariogeneration Authors.

  Example how to create a more customized a junction with different widths of lanes,
  using generators and LaneDef with different lane widths

  Some features used

  - CommonJunctionCreator

  - DirectJunctionCreator

  - LaneDef

  - create_road

  - adjust_roadmarks
"""

from scenariogeneration import xodr, prettyprint, ScenarioGenerator
import numpy as np
import os


class Scenario(ScenarioGenerator):
    def __init__(self):
        super().__init__()

    def road(self, **kwargs):
        # create a road with some strange lane sections
        road1 = xodr.create_road(
            xodr.Line(195),
            1,
            [
                xodr.LaneDef(
                    13,
                    80,
                    3,
                    4,
                    3,
                    lane_start_widths=[3, 3, 3],
                    lane_end_widths=[3, 3, 3, 3],
                ),
                xodr.LaneDef(
                    120,
                    140,
                    4,
                    3,
                    2,
                    lane_start_widths=[3, 3, 3, 3],
                    lane_end_widths=[3, 3, 3],
                ),
            ],
            [
                xodr.LaneDef(
                    13,
                    80,
                    3,
                    4,
                    -1,
                    lane_start_widths=[3, 3, 3],
                    lane_end_widths=[3, 3, 3, 3],
                ),
                xodr.LaneDef(
                    120,
                    140,
                    4,
                    3,
                    -4,
                    lane_start_widths=[3, 3, 3, 3],
                    lane_end_widths=[3, 3, 3],
                ),
            ],
            center_road_mark=xodr.std_roadmark_broken_broken(),
        )

        # create more roads
        road2 = xodr.create_road(
            xodr.Line(103),
            2,
            xodr.LaneDef(40, 80, 3, 3, lane_start_widths=[3, 3, 3]),
            3,
            center_road_mark=xodr.std_roadmark_broken_broken(),
        )

        road3 = xodr.create_road(xodr.Spiral(0.00001, 0.01, 100), 3, 3, 0)
        road4 = xodr.create_road(xodr.Spiral(-0.0001, -0.01, 100), 4, 0, 3)

        road5 = xodr.create_road(
            xodr.Line(100),
            5,
            xodr.LaneDef(40, 80, 3, 3, lane_start_widths=[3, 3, 3]),
            3,
            center_road_mark=xodr.std_roadmark_broken_broken(),
        )
        road6 = xodr.create_road(
            xodr.Line(100),
            6,
            xodr.LaneDef(40, 80, 3, 3, lane_start_widths=[3, 3, 3]),
            3,
            center_road_mark=xodr.std_roadmark_broken_broken(),
        )

        # connect all roads
        road1.add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.start)
        road1.add_predecessor(xodr.ElementType.junction, 100)

        road2.add_predecessor(xodr.ElementType.road, 1, xodr.ContactPoint.end)

        road3.add_predecessor(xodr.ElementType.junction, 100)
        road4.add_predecessor(xodr.ElementType.junction, 100)

        # create a direct junction
        junc = xodr.DirectJunctionCreator(100, "direct_junction")

        junc.add_connection(road1, road3)
        junc.add_connection(road1, road4)

        # create a common junction
        junc2 = xodr.CommonJunctionCreator(200, "common junction")
        junc2.add_incoming_road_cartesian_geometry(
            road2, 0, 0, -3.14 * 3 / 2, "successor"
        )
        junc2.add_incoming_road_cartesian_geometry(
            road5, 30, 20, -3.14, "successor"
        )
        junc2.add_incoming_road_cartesian_geometry(
            road6, -30, 20, 0, "predecessor"
        )

        junc2.add_connection(2, 5)
        junc2.add_connection(2, 6)

        # add everything to the OpenDRIVE object
        odr = xodr.OpenDrive("my adjusted road")
        odr.add_road(road1)
        odr.add_road(road2)
        odr.add_road(road3)
        odr.add_road(road4)
        odr.add_road(road5)
        odr.add_road(road6)
        odr.add_junction_creator(junc)
        odr.add_junction_creator(junc2)

        # adjust roads and lanes
        odr.adjust_roads_and_lanes()

        # adjust roadmarks (comment out to see difference)
        odr.adjust_roadmarks()
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
