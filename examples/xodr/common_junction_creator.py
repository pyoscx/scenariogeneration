"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.


    Example of how to create a highway entry using CommonJunctionCreator

    Some features used:

    - create_road

    - add_successor/add_predecessor with and without the lane_offset option, and the direct_junction input

    - CommonJunctionCreator
"""

import os
from scenariogeneration import xodr

# initalize the junction creator
junction_id = 100
junction_creator = xodr.DirectJunctionCreator(id=junction_id, name="my direct junction")

# create 3 roads, and add the successor/predecessor junction

road1 = xodr.create_road(xodr.Line(100), id=1, left_lanes=2, right_lanes=2)
road2 = xodr.create_road(xodr.Line(100), id=2, left_lanes=1, right_lanes=1)
road3 = xodr.create_road(xodr.Line(100), id=3, left_lanes=2, right_lanes=2)

# create direct junction connection to all common lanes between the main roads

junction_creator = xodr.CommonJunctionCreator(id=100, name="my_junction")

junction_creator.add_incoming_road_cartesian_geometry(
    road1, x=0, y=0, heading=0, road_connection="successor"
)

junction_creator.add_incoming_road_cartesian_geometry(
    road2, x=50, y=50, heading=3.1415 * 3 / 2, road_connection="predecessor"
)

junction_creator.add_incoming_road_cartesian_geometry(
    road3, x=100, y=0, heading=-3.1415, road_connection="predecessor"
)


# create the opendrive
odr = xodr.OpenDrive("my_road")

# add the roads
junction_creator.add_connection(road_one_id=1, road_two_id=3)
junction_creator.add_connection(
    road_one_id=1, road_two_id=2, lane_one_id=2, lane_two_id=1
)
junction_creator.add_connection(
    road_one_id=2, road_two_id=3, lane_one_id=-1, lane_two_id=2
)

odr.add_road(road1)
odr.add_road(road2)
odr.add_road(road3)

# add the junction creator
odr.add_junction_creator(junction_creator)

# adjust the roads and lanes
odr.adjust_roads_and_lanes()

# write the OpenDRIVE file as xodr using current script name
odr.write_xml(os.path.basename(__file__).replace(".py", ".xodr"))

# uncomment the following lines to display the road using esmini
# from scenariogeneration import esmini
# esmini(odr,os.path.join('esmini'))
