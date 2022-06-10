"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.


    Example of how to create a highway exits using DirectJunctionCreator

    Some features used:

    - create_road

    - add_successor/add_predecessor with and without the lane_offset option, and the direct_junction input

    - DirectJunctionCreator
"""

import os
from scenariogeneration import xodr

# initalize the junction creator
junction_id = 100
junction_creator = xodr.DirectJunctionCreator(id=junction_id, name="my direct junction")

# create 4 roads, and add the successor/predecessor junction
start_road = xodr.create_road([xodr.Line(200)], id=1, left_lanes=2, right_lanes=3)
start_road.add_successor(xodr.ElementType.junction, junction_id)

continuation_road = xodr.create_road(
    [xodr.Line(200)], id=2, left_lanes=3, right_lanes=2
)
continuation_road.add_predecessor(xodr.ElementType.junction, junction_id)

exit_road_right = xodr.create_road(
    xodr.Spiral(-0.00001, -0.001, 100), id=10, left_lanes=0, right_lanes=1
)
exit_road_right.add_predecessor(xodr.ElementType.junction, junction_id)

exit_road_left = xodr.create_road(
    xodr.Spiral(0.01, 0.0001, 150), id=20, left_lanes=1, right_lanes=0
)
exit_road_left.add_successor(xodr.ElementType.junction, junction_id)

# create direct junction connection to all common lanes between the main roads
junction_creator.add_connection(incoming_road=start_road, linked_road=continuation_road)

# create the connection to the exit roads with only the specific lanes
junction_creator.add_connection(
    incoming_road=start_road,
    linked_road=exit_road_right,
    incoming_lane_ids=-3,
    linked_lane_ids=-1,
)
junction_creator.add_connection(
    incoming_road=exit_road_left,
    linked_road=continuation_road,
    incoming_lane_ids=1,
    linked_lane_ids=3,
)


# create the opendrive
odr = xodr.OpenDrive("my_road")

# add the roads
odr.add_road(start_road)
odr.add_road(continuation_road)
odr.add_road(exit_road_right)
odr.add_road(exit_road_left)

# add the junction creator
odr.add_junction_creator(junction_creator)

# adjust the roads and lanes
odr.adjust_roads_and_lanes()

# write the OpenDRIVE file as xodr using current script name
odr.write_xml(os.path.basename(__file__).replace(".py", ".xodr"))

# uncomment the following lines to display the road using esmini
# from scenariogeneration import esmini
# esmini(odr,os.path.join('esmini'))
