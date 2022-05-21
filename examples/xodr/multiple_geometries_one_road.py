"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.
  
    Fundamental example how to build up a road from scratch.

    This example should be seen as a developer example how roads are built up from the very basic classes in OpenDRIVE
    create_road will take care of this and much more, so a user is recommended to use that generator instead.

    Some features used:

    - PlanView

    - Lane

    - Lanes

    - LaneSection

    - RoadMark

    - Road

"""
from scenariogeneration import xodr, prettyprint
import numpy as np
import os


## Multiple geometries in one only road.

##1. Create the planview
planview = xodr.PlanView()

##2. Create some geometries and add them to the planview
line1 = xodr.Line(100)
arc1 = xodr.Arc(0.05, angle=np.pi / 2)
line2 = xodr.Line(100)
cloth1 = xodr.Spiral(0.05, -0.1, 30)
line3 = xodr.Line(100)

planview.add_geometry(line1)
planview.add_geometry(arc1)
planview.add_geometry(line2)
planview.add_geometry(cloth1)
planview.add_geometry(line3)


##3. Create a solid roadmark
rm = xodr.RoadMark(xodr.RoadMarkType.solid, 0.2)

##4. Create centerlane
centerlane = xodr.Lane(a=2)
centerlane.add_roadmark(rm)

##5. Create lane section form the centerlane
lanesec = xodr.LaneSection(0, centerlane)

##6. Create left and right lanes
lane2 = xodr.Lane(a=3)
lane2.add_roadmark(rm)
lane3 = xodr.Lane(a=3)
lane3.add_roadmark(rm)

##7. Add lanes to lane section
lanesec.add_left_lane(lane2)
lanesec.add_right_lane(lane3)

##8. Add lane section to Lanes
lanes = xodr.Lanes()
lanes.add_lanesection(lanesec)

##9. Create Road from Planview and Lanes
road = xodr.Road(1, planview, lanes)

##10. Create the OpenDrive class (Master class)
odr = xodr.OpenDrive("myroad")

##11. Finally add roads to Opendrive
odr.add_road(road)

##12. Adjust initial positions of the roads looking at succ-pred logic
odr.adjust_roads_and_lanes()

##13. Print the .xodr file
prettyprint(odr.get_element())

# write the OpenDRIVE file as xodr using current script name
odr.write_xml(os.path.basename(__file__).replace(".py", ".xodr"))

# uncomment the following lines to display the road using esmini
# from scenariogeneration import esmini
# esmini(odr,os.path.join('esmini'))
