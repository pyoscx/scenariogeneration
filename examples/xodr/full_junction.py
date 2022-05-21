"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.
  
    An example, using the generators, showing how to create different types of junctions


    All the roads in a junction are formed by clothoid-arc-clothoid geotrietries
    In this example we can create a junction given

        option1. the distance R of every road from the center of the junction - R can change for each road

        option2. the radius of the inner arc geometry - for this case you can only use
                                                        numintersections = 3 or 4
                                                        angles = [0,np.pi/2, 3*np.pi/2] or [0, np.pi/2, np.pi, 3*np.pi/2]
    Some features used:

    - create_straight_road

    - create_junction_roads

    - create_junction
"""

import numpy as np
import os
from scenariogeneration import xodr

roads = []
numintersections = 3
angles = []
nlanes = 1
for i in range(numintersections):
    # roads.append(xodr.create_straight_road(i,n_lanes=1))
    roads.append(
        xodr.create_road(
            [xodr.Line(100)],
            i,
            center_road_mark=xodr.STD_ROADMARK_BROKEN,
            left_lanes=nlanes,
            right_lanes=nlanes,
        )
    )
    # use this instead to change the number of lanes in the crossing
    # roads.append(xodr.generators.create_straight_road(i, length=100, junction=-1, n_lanes=5, lane_offset=3))
    angles.append(i * 2 * np.pi / numintersections)

# use this for a T-crossing instead
# angles = [0, np.pi/2, 3*np.pi/2]

# use this non perpendicular crossing
angles = [0, 1.3 * np.pi / 2, 3.2 * np.pi / 2]

# option 1. uncomment this if you want to create the junction from the distance R of every road from the center of the junction
junction_roads = xodr.create_junction_roads(roads, angles, [20])
# option 2. creation of junction given the radius of the inner arc geometry
# junction_roads = xodr.create_junction_roads_from_arc(roads,angles,8)

# create the junction
junction = xodr.create_junction(junction_roads, 1, roads)

# create the opendrive and add all roads and the junction

odr = xodr.OpenDrive("myroad")

odr.add_junction(junction)

for r in roads:
    odr.add_road(r)

for j in junction_roads:
    odr.add_road(j)

odr.adjust_roads_and_lanes()

# write the OpenDRIVE file as xodr using current script name
odr.write_xml(os.path.basename(__file__).replace(".py", ".xodr"))

# uncomment the following lines to display the road using esmini
# from scenariogeneration import esmini
# esmini(odr,os.path.join('esmini'))
