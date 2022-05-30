"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.
  
    Example for linking two roads with an unequal number of lanes.

    Note: This is possible and valid according to the OpenDRIVE standard. It is
    sometimes necessary to use this approach but it might often be prefered to begin
    a new lane section to change the number of lanes instead.
"""

from scenariogeneration import xodr
import os

# Create roads
length_road = 100.0
road_first = xodr.create_road([xodr.Line(length_road)], 1, 2, 3)
road_second = xodr.create_road([xodr.Line(length_road)], 2, 2, 4)
# Make a new lane open up/branch out
new_lane_width = 3.0
road_second.lanes.lanesections[0].rightlanes[2].a = 0.0
road_second.lanes.lanesections[0].rightlanes[2].b = 0.0
road_second.lanes.lanesections[0].rightlanes[2].c = (
    3.0 / length_road**2 * new_lane_width
)
road_second.lanes.lanesections[0].rightlanes[2].d = (
    -2.0 / length_road**3 * new_lane_width
)

## Create the OpenDrive class (Master class)
odr = xodr.OpenDrive("myroads")

## Finally add roads to Opendrive
odr.add_road(road_first)
odr.add_road(road_second)

# Link roads
road_first.add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.start)
road_second.add_predecessor(xodr.ElementType.road, 1, xodr.ContactPoint.end)

# Link lanes but do not link the newly beginning lane
link_lane_ids_first = [2, 1, -1, -2, -3]
link_lane_ids_second = [2, 1, -1, -2, -4]
xodr.create_lane_links_from_ids(
    road_first, road_second, link_lane_ids_first, link_lane_ids_second
)

# Adjust initial positions of the roads looking at succ-pred logic
odr.adjust_startpoints()

# write the OpenDRIVE file as xodr using current script name
odr.write_xml(os.path.basename(__file__).replace(".py", ".xodr"))
