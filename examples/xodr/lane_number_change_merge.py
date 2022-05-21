"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.

    Example how to create a road with a lanemerge.

    Simple cases can automated with create_road and LaneDef, but for complex cases this example shows how to do it from scratch.
    This example makes use of the LaneLinker class that is not part of OpenDRIVE but a helper class for the xodr module

    Some features used:

    - PlanView

    - RoadMark

    - Lane

    - LaneSection

    - Lanes

    - LaneLinker
"""


from scenariogeneration import xodr
import os

# create the planview and the geometry
planview = xodr.PlanView()


planview.add_geometry(xodr.Line(500))


# create two different roadmarkings
rm_solid = xodr.RoadMark(xodr.RoadMarkType.solid, 0.2)
rm_dashed = xodr.RoadMark(xodr.RoadMarkType.broken, 0.2)

# create a centerlane (same centerlane can be used since no linking is needed for this)
centerlane = xodr.Lane(a=2)
centerlane.add_roadmark(rm_solid)

# create the first lanesection with two lanes
lanesec1 = xodr.LaneSection(0, centerlane)
lane1 = xodr.Lane(a=3)
lane1.add_roadmark(rm_dashed)

lane2 = xodr.Lane(a=3)
lane2.add_roadmark(rm_solid)

lanesec1.add_right_lane(lane1)
lanesec1.add_right_lane(lane2)

# create the second lanesection with one lane merging
lanesec2 = xodr.LaneSection(250, centerlane)
lane3 = xodr.Lane(a=3)
lane3.add_roadmark(rm_dashed)

lane4 = xodr.Lane(a=3, b=-0.1)
lane4.add_roadmark(rm_solid)

lanesec2.add_right_lane(lane3)
lanesec2.add_right_lane(lane4)

# create the last lanesection with one lane
lanesec3 = xodr.LaneSection(280, centerlane)

lane5 = xodr.Lane(a=3)
lane5.add_roadmark(rm_solid)

lanesec3.add_right_lane(lane5)

# create the lane links
lanelinker = xodr.LaneLinker()
lanelinker.add_link(predlane=lane1, succlane=lane3)
lanelinker.add_link(predlane=lane2, succlane=lane4)
lanelinker.add_link(predlane=lane3, succlane=lane5)

# create the lanes with the correct links
lanes = xodr.Lanes()
lanes.add_lanesection(lanesec1, lanelinker)
lanes.add_lanesection(lanesec2, lanelinker)
lanes.add_lanesection(lanesec3, lanelinker)

# create the road
road = xodr.Road(1, planview, lanes)

# create the opendrive
odr = xodr.OpenDrive("myroad")
odr.add_road(road)

# adjust the roads and lanes
odr.adjust_roads_and_lanes()

# write the OpenDRIVE file as xodr using current script name
odr.write_xml(os.path.basename(__file__).replace(".py", ".xodr"))

# uncomment the following lines to display the road using esmini
# from scenariogeneration import esmini
# esmini(odr,os.path.join('esmini'))
