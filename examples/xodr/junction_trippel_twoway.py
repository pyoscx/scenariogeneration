"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.
  
  This example shows how to make a very simple junction from "scratch" without using any generators.

    NOTE: This is more of a reference example and should not be considered a "user example" more of a "developer example".


"""
from scenariogeneration import xodr
import numpy as np
import os


rm = xodr.RoadMark(xodr.RoadMarkType.solid, 0.2)

# create geometries

geoms = []
geoms.append(xodr.Line(100))
geoms.append(xodr.Spiral(0.001, 0.019, 30))
geoms.append(xodr.Line(100))
geoms.append(xodr.Spiral(-0.001, -0.1, 30))
geoms.append(xodr.Line(100))
geoms.append(xodr.Line(20))
geoms.append(xodr.Line(100))
numberofroads = len(geoms)

# create planviews
planviews = []
for g in geoms:
    pv = xodr.PlanView()
    pv.add_geometry(g)
    planviews.append(pv)


# create centerlanes
lanecenters = []
for i in range(numberofroads):
    lc = xodr.Lane(a=3)
    lc.add_roadmark(rm)
    lanecenters.append(lc)

# create lanes
rightlanes = []
leftlanes = []
for i in range(numberofroads):
    right = xodr.Lane(a=3)
    right.add_roadmark(rm)
    rightlanes.append(right)
    left = xodr.Lane(a=3)
    left.add_roadmark(rm)
    leftlanes.append(left)

# create lanesections
lanesections = []
for i in range(numberofroads):
    lsec = xodr.LaneSection(0, lanecenters[i])
    lsec.add_right_lane(rightlanes[i])
    lsec.add_left_lane(leftlanes[i])
    lanesections.append(lsec)

## create lanes
lanes = []
for l in lanesections:
    lanes1 = xodr.Lanes()
    lanes1.add_lanesection(l)
    lanes.append(lanes1)


# finally create the roads
roads = []
roadtypes = [-1, 1, -1, 1, -1, 1, -1]
for i in range(numberofroads):
    roads.append(xodr.Road(i, planviews[i], lanes[i], road_type=roadtypes[i]))

roads[0].add_successor(xodr.ElementType.junction, 1)

roads[1].add_predecessor(xodr.ElementType.road, 0, xodr.ContactPoint.end)
roads[1].add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.start)

roads[2].add_predecessor(xodr.ElementType.junction, 1)

roads[3].add_predecessor(xodr.ElementType.road, 0, xodr.ContactPoint.end)
roads[3].add_successor(xodr.ElementType.road, 4, xodr.ContactPoint.start)

roads[4].add_predecessor(xodr.ElementType.junction, 1)

roads[5].add_predecessor(xodr.ElementType.road, 0, xodr.ContactPoint.end)
roads[5].add_successor(xodr.ElementType.road, 6, xodr.ContactPoint.start)

roads[6].add_predecessor(xodr.ElementType.junction, 1)

# create the opendrive
odr = xodr.OpenDrive("myroad")
for r in roads:
    odr.add_road(r)

# create junction
junction = xodr.Junction("test", 1)
con1 = xodr.Connection(0, 1, xodr.ContactPoint.start)
con1.add_lanelink(-1, -1)
con2 = xodr.Connection(0, 3, xodr.ContactPoint.start)
con2.add_lanelink(-1, -1)
con3 = xodr.Connection(0, 5, xodr.ContactPoint.start)
con3.add_lanelink(-1, -1)

con4 = xodr.Connection(2, 1, xodr.ContactPoint.end)
con4.add_lanelink(1, 1)
con5 = xodr.Connection(4, 3, xodr.ContactPoint.end)
con5.add_lanelink(1, 1)
con6 = xodr.Connection(6, 5, xodr.ContactPoint.end)
con6.add_lanelink(1, 1)

junction.add_connection(con1)
junction.add_connection(con2)
junction.add_connection(con3)
junction.add_connection(con4)
junction.add_connection(con5)
junction.add_connection(con6)

# odr.create_junction()
odr.add_junction(junction)
odr.adjust_roads_and_lanes()
# xodr.prettyprint(odr.get_element())

# write the OpenDRIVE file as xodr using current script name
odr.write_xml(os.path.basename(__file__).replace(".py", ".xodr"))

# uncomment the following lines to display the road using esmini
# from scenariogeneration import esmini
# esmini(odr,os.path.join('esmini'))
