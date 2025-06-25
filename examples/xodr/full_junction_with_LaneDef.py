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

  - LaneDef

  - create_road
"""

import os

import numpy as np

from scenariogeneration import ScenarioGenerator, prettyprint, xodr


class Scenario(ScenarioGenerator):
    def __init__(self):
        super().__init__()

    def road(self, **kwargs):
        # create 4 roads going into a junction with different lanewidths
        road1 = xodr.create_road(
            xodr.Line(100),
            1,
            xodr.LaneDef(0, 100, 2, 2, None, [3, 1]),
            xodr.LaneDef(0, 100, 2, 2, None, [4, 1]),
        )
        road2 = xodr.create_road(
            xodr.Line(100), 2, 0, [xodr.LaneDef(0, 100, 2, 2, None, [2, 2])]
        )
        road3 = xodr.create_road(
            xodr.Line(100), 3, [xodr.LaneDef(0, 100, 2, 2, None, [4, 4])], 0
        )
        road4 = xodr.create_road(
            xodr.Line(100),
            4,
            [xodr.LaneDef(0, 100, 2, 2, None, [3, 3])],
            [xodr.LaneDef(0, 100, 2, 2, None, [4, 4])],
        )

        # create the connection in the junction
        jc = xodr.CommonJunctionCreator(100, "my junc")
        jc.add_incoming_road_cartesian_geometry(
            road1, 0, -20, -np.pi / 2 * 3, "successor"
        )
        jc.add_incoming_road_cartesian_geometry(
            road4, 5, 30, -np.pi / 2 - 0.1, "successor"
        )
        jc.add_incoming_road_cartesian_geometry(
            road3, -20, 0, 0, "predecessor"
        )
        jc.add_incoming_road_cartesian_geometry(
            road2, 20, 0, np.pi, "predecessor"
        )

        jc.add_connection(1, 2)
        jc.add_connection(3, 1)
        jc.add_connection(1, 4, [-1, 1], [1, -1])
        jc.add_connection(2, 3)
        jc.add_connection(4, 2)
        jc.add_connection(4, 3)

        # create the open drive and add the roads
        odr = xodr.OpenDrive("my test road")
        odr.add_road(road1)
        odr.add_road(road2)
        odr.add_road(road3)
        odr.add_road(road4)
        odr.add_junction_creator(jc)

        # adjust roads and lanes
        odr.adjust_roads_and_lanes()

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
