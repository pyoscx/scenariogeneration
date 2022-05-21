"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.
  
    Example showing how to create two separate roads (that are not linked), hence adjust_roads_and_lanes will not be able to set the geometries without a similar approach.

    Some features used:

    - PlanView


"""
from scenariogeneration import xodr, prettyprint
import numpy as np
import os


odr = xodr.OpenDrive("myroad")

# ---------------- Road 1
planview = xodr.PlanView(0, 0, 0)

# create some geometries and add to the planview
planview.add_geometry(xodr.Line(100))

# create a solid roadmark
rm = xodr.RoadMark(xodr.RoadMarkType.solid, 0.2)

# create centerlane
centerlane_1 = xodr.Lane(a=2)
centerlane_1.add_roadmark(rm)
lanesec_1 = xodr.LaneSection(0, centerlane_1)

# add a driving lane
lane2_1 = xodr.Lane(a=3.1)
lane2_1.add_roadmark(rm)
lanesec_1.add_left_lane(lane2_1)

lane3_1 = xodr.Lane(a=3.1)
lane3_1.add_roadmark(rm)
lanesec_1.add_right_lane(lane3_1)

## finalize the road
lanes_1 = xodr.Lanes()
lanes_1.add_lanesection(lanesec_1)

road = xodr.Road(1, planview, lanes_1)


odr.add_road(road)


# ---------------- Road 2

planview2 = xodr.PlanView(x_start=0, y_start=10, h_start=np.pi / 2)
# planview2 = xodr.PlanView()

# create some geometries and add to the planview
planview2.add_geometry(xodr.Line(200))

# create a solid roadmark
rm = xodr.RoadMark(xodr.RoadMarkType.solid, 0.2)

# create centerlane
centerlane = xodr.Lane(a=2)
centerlane.add_roadmark(rm)
lanesec = xodr.LaneSection(0, centerlane)

# add a driving lane
lane2 = xodr.Lane(a=3.1)
lane2.add_roadmark(rm)
lanesec.add_left_lane(lane2)

lane3 = xodr.Lane(a=3.1)
lane3.add_roadmark(rm)
lanesec.add_right_lane(lane3)

## finalize the road
lanes = xodr.Lanes()
lanes.add_lanesection(lanesec)

road2 = xodr.Road(2, planview2, lanes)

odr.add_road(road2)


# ------------------ Finalize
odr.adjust_roads_and_lanes()
prettyprint(odr.get_element())

# write the OpenDRIVE file as xodr using current script name
odr.write_xml(os.path.basename(__file__).replace(".py", ".xodr"))

# uncomment the following lines to display the road using esmini
from scenariogeneration import esmini

# esmini(odr,os.path.join('/home/mander76/local/scenario_creation/esmini'))


# uncomment the following lines to display the road using esmini
# from scenariogeneration import esmini
# esmini(odr,os.path.join('esmini'))
