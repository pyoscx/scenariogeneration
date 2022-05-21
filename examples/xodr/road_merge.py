"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.
  
    Example how to create a simple road merge through a junction

    Some features used

    - create_road

    - add_successor/add_predecessor with lane_offset

    - create_junction

"""
from scenariogeneration import xodr

import os

# create some roads
roads = []
roads.append(xodr.create_road(xodr.Line(100), id=0, left_lanes=1, right_lanes=2))
roads.append(xodr.create_road(xodr.Line(100), id=1, left_lanes=0, right_lanes=1))
roads.append(xodr.create_road(xodr.Line(100), id=2, left_lanes=1, right_lanes=3))
roads.append(
    xodr.create_road(
        xodr.Spiral(0.001, 0.02, 30), id=3, left_lanes=1, right_lanes=2, road_type=1
    )
)
roads.append(
    xodr.create_road(
        xodr.Spiral(-0.001, -0.02, 30), id=4, left_lanes=0, right_lanes=1, road_type=1
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


junction = xodr.create_junction(roads[3:], 1, roads[0:3])


# create the opendrive
odr = xodr.OpenDrive("myroad")
for r in roads:
    odr.add_road(r)
odr.adjust_roads_and_lanes()
odr.add_junction(junction)

# write the OpenDRIVE file as xodr using current script name
odr.write_xml(os.path.basename(__file__).replace(".py", ".xodr"))

# uncomment the following lines to display the road using esmini
# from scenariogeneration import esmini
# esmini(odr,os.path.join('esmini'))
