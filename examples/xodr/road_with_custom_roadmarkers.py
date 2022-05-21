"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.
  
    Example how to create roads with customized centerline for double road markers

    Some features used

    - PlanView

    - LaneSection

    - RoadMark

    - RoadLine

"""


import os
from scenariogeneration import xodr


# create a simple planview
planview = xodr.PlanView()
planview.add_geometry(xodr.Line(300))

## create the customized centerlanes with different lanemarkings
centerlanes = []
# standard solid solid

solid_solid = xodr.Lane()
solid_solid.add_roadmark(xodr.STD_ROADMARK_SOLID_SOLID)
centerlanes.append(solid_solid)

# standard solid broken
solid_broken = xodr.Lane()
solid_broken.add_roadmark(xodr.STD_ROADMARK_SOLID_BROKEN)
centerlanes.append(solid_broken)

# customized broken broken
broken_broken_roadmark = xodr.RoadMark(xodr.RoadMarkType.broken_broken)
broken_broken_roadmark.add_specific_road_line(xodr.RoadLine(0.2, 9, 3, 0.2))
broken_broken_roadmark.add_specific_road_line(xodr.RoadLine(0.2, 3, 9, -0.2, 3))
broken_broken = xodr.Lane()
broken_broken.add_roadmark(broken_broken_roadmark)
centerlanes.append(broken_broken)


# create the different lanesections and add them to the lanes
lanes = xodr.Lanes()
ls_start = 0
for i in centerlanes:
    lanesection = xodr.LaneSection(ls_start, i)
    left_lane_with_roadmark = xodr.Lane(a=4)
    left_lane_with_roadmark.add_roadmark(xodr.STD_ROADMARK_BROKEN)

    right_lane_with_roadmark = xodr.Lane(a=4)
    right_lane_with_roadmark.add_roadmark(xodr.STD_ROADMARK_SOLID)
    lanesection.add_left_lane(left_lane_with_roadmark)
    lanesection.add_right_lane(right_lane_with_roadmark)
    ls_start += 100

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
