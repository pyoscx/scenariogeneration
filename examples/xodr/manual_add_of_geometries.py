"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.
  
    Example how to add geometries with a fixed position, please note that *adjust_roads_and_lanes* will only take care of the lane linking in this case not any geometrical adjustmensts

    This is how a road can be built up if all exact postions of the geometries are already known

    Some features used:

    - PlanView

    - (PlanView).add_fixed_geometry

    - RoadMark

    - Lane

    - LaneSection

    - Lanes

    - LaneLinker
"""

import os
from scenariogeneration import xodr, xosc, esmini, prettyprint, ScenarioGenerator

planview = xodr.PlanView()


# add two geometries based on exact position
planview.add_fixed_geometry(xodr.Line(100), 0, 0, 0)
planview.add_fixed_geometry(xodr.Arc(0.01, length=100), 100, 0, 0)

# create simple lanes
lanes = xodr.Lanes()
lanesection1 = xodr.LaneSection(0, xodr.standard_lane())
lanesection1.add_left_lane(xodr.standard_lane(rm=xodr.STD_ROADMARK_SOLID))
lanesection1.add_right_lane(xodr.standard_lane(rm=xodr.STD_ROADMARK_SOLID))
lanes.add_lanesection(lanesection1)


road1 = xodr.Road(0, planview, lanes)

# create a simple second road for connection
road2 = xodr.create_road(xodr.Line(100), 1)

# connect the roads with successor/predecessor
road1.add_successor(xodr.ElementType.road, 1, xodr.ContactPoint.start)
road2.add_predecessor(xodr.ElementType.road, 0, xodr.ContactPoint.end)

odr = xodr.OpenDrive("my_road")
odr.add_road(road1)
odr.add_road(road2)

# will adjust the second road and the lanes and lane links correctly
odr.adjust_roads_and_lanes()


odr.write_xml(os.path.basename(__file__).replace(".py", ".xodr"))

# uncomment the following lines to display the road using esmini
# from scenariogeneration import esmini
# esmini(odr,os.path.join('esmini'))
