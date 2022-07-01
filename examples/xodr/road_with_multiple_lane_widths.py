"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.
  
    Example how to create a more customized road with different widths 

    Some features used

    - create_road

    - add_lane_width

"""
from scenariogeneration import xodr

import os

# create a normal road

road = xodr.create_road(xodr.Line(200), id=0, lane_width=3)

road.lanes.lanesections[0].leftlanes[0].add_lane_width(a=3, b=2, soffset=100)
road.lanes.lanesections[0].leftlanes[0].add_lane_width(a=5, b=0, soffset=150)

# create the opendrive
odr = xodr.OpenDrive("myroad")

odr.add_road(road)
odr.adjust_roads_and_lanes()


# write the OpenDRIVE file as xodr using current script name
odr.write_xml(os.path.basename(__file__).replace(".py", ".xodr"))

# uncomment the following lines to display the road using esmini
# from scenariogeneration import esmini
# esmini(odr,os.path.join('esmini'))
