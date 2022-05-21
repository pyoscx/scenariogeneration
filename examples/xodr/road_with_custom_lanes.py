"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.
  
    Example how to create roads with custom lanes to the left and right

    Some features used

    - PlanView

    - LaneSection

"""
import os
from scenariogeneration import xodr


# create a simple planview
planview = xodr.PlanView()
planview.add_geometry(xodr.Line(500))

# create the customized lanes
centerlane = xodr.Lane(lane_type=xodr.LaneType.median)
lanesection = xodr.LaneSection(0, centerlane)

# add the median to the center
lanesection.add_left_lane(xodr.Lane(lane_type=xodr.LaneType.median, a=0.3))
lanesection.add_right_lane(xodr.Lane(lane_type=xodr.LaneType.median, a=0.3))

# add a curb
lanesection.add_left_lane(xodr.Lane(lane_type=xodr.LaneType.curb, a=0.1))
lanesection.add_right_lane(xodr.Lane(lane_type=xodr.LaneType.curb, a=0.1))

# add driving lanes with roadmarks
left_lane_with_roadmark = xodr.Lane(a=4)
left_lane_with_roadmark.add_roadmark(xodr.STD_ROADMARK_BROKEN)
lanesection.add_left_lane(left_lane_with_roadmark)

right_lane_with_roadmark = xodr.Lane(a=4)
right_lane_with_roadmark.add_roadmark(xodr.STD_ROADMARK_SOLID)
lanesection.add_right_lane(right_lane_with_roadmark)

# add driving lanes to end in border
lanesection.add_left_lane(xodr.Lane(a=4))
lanesection.add_right_lane(xodr.Lane(a=4))

# add a border

lanesection.add_left_lane(xodr.Lane(lane_type=xodr.LaneType.border, a=0.2))
lanesection.add_right_lane(xodr.Lane(lane_type=xodr.LaneType.border, a=0.2))

# add a final curb
lanesection.add_left_lane(xodr.Lane(lane_type=xodr.LaneType.curb, a=0.1))
lanesection.add_right_lane(xodr.Lane(lane_type=xodr.LaneType.curb, a=0.1))

# add a bikingroad on one side
lanesection.add_right_lane(xodr.Lane(lane_type=xodr.LaneType.biking, a=2))

# create the lanes and add the lanesection
lanes = xodr.Lanes()
lanes.add_lanesection(lanesection)

# create the road
road = xodr.Road(0, planview, lanes)

# create the opendrive and add the road
odr = xodr.OpenDrive("road with custom lanes")
odr.add_road(road)

# adjust the road
odr.adjust_roads_and_lanes()

# write the OpenDRIVE file as xodr using current script name
odr.write_xml(os.path.basename(__file__).replace(".py", ".xodr"))

# uncomment the following lines to display the road using esmini
# from scenariogeneration import esmini
# esmini(odr,os.path.join('esmini'))
