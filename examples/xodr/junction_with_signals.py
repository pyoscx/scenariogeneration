"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.
  
    Example of how to create a junction but adding signals to the junction


"""

# Same approach to creating a junction as "full_junction.py" but with signals for each incoming road.
import numpy as np
import os
from scenariogeneration import xodr


roads = []
incoming_roads = 4
angles = []
for i in range(incoming_roads):
    roads.append(xodr.create_straight_road(i))
    # use this instead to change the number of lanes in the crossing
    # roads.append(xodr.generators.create_straight_road(i, length=100, junction=-1, n_lanes=2, lane_offset=3))
    angles.append(i * 2 * np.pi / incoming_roads)
    if angles[-1] == 0:
        roads[-1].add_signal(
            xodr.Signal(s=98.0, t=-4, country="USA", Type="R1", subtype="1")
        )
    else:
        roads[-1].add_signal(
            xodr.Signal(
                s=2.0,
                t=4,
                country="USA",
                Type="R1",
                subtype="1",
                orientation=xodr.Orientation.negative,
            )
        )


# use this for a T-crossing instead
# angles = [0,np.pi/2, 3*np.pi/2]

# print(roads)
junc = xodr.create_junction_roads(roads, angles, [8])
odr = xodr.OpenDrive("myroad")
junction = xodr.create_junction(junc, 1, roads)

odr.add_junction(junction)
for r in roads:
    odr.add_road(r)
for j in junc:
    odr.add_road(j)

odr.adjust_roads_and_lanes()

# write the OpenDRIVE file as xodr using current script name
odr.write_xml(os.path.basename(__file__).replace(".py", ".xodr"))

# uncomment the following lines to display the road using esmini
# from scenariogeneration import esmini
# esmini(odr,os.path.join('esmini'))
