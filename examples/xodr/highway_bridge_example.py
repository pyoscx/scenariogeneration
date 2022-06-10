"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.

    Example of how to create a highway with a bridge using DirectJunctionCreator, and CommonJunctionCreator

    Some features used:

    - create_road

    - add_successor/add_predecessor with and without the lane_offset option, and the direct_junction input

    - DirectJunctionCreator

    - CommonJunctionCreator
"""


from scenariogeneration import xodr
import numpy as np
import os

# create two CommonJunctionCreators for junctions connecting the bridge

junction_creator_right = xodr.CommonJunctionCreator(
    id=100, name="right_junction", startnum=100
)
junction_creator_left = xodr.CommonJunctionCreator(
    id=200, name="left_junction", startnum=200
)

# create two DirectJunctionCreators for the highway connections

junction_creator_direct_first = xodr.DirectJunctionCreator(
    id=300, name="first_highway_connection"
)
junction_creator_direct_second = xodr.DirectJunctionCreator(
    id=400, name="second_highway_connection"
)

# create the highway roads

road_highway_1 = xodr.create_road(
    xodr.Spiral(0.001, 0.000001, 300), 1, right_lanes=3, left_lanes=3
)
road_highway_2 = xodr.create_road(xodr.Line(140), 2, right_lanes=2, left_lanes=2)
road_highway_3 = xodr.create_road(xodr.Line(200), 3, right_lanes=3, left_lanes=3)

# create the entry and exit roads

exit_road1 = xodr.create_road(
    [xodr.Arc(-0.05, angle=np.pi / 2), xodr.Arc(0.05, angle=np.pi / 2)],
    10,
    right_lanes=0,
    left_lanes=1,
)
exit_road1.add_elevation(0, 10, -10 / (40 * np.pi / 2), 0, 0)

entry_road1 = xodr.create_road(
    [xodr.Arc(0.05, angle=np.pi / 2), xodr.Arc(-0.05, angle=np.pi / 2)],
    20,
    left_lanes=1,
    right_lanes=0,
)
entry_road1.add_elevation(0, 0, 10 / (40 * np.pi / 2), 0, 0)

exit_road2 = xodr.create_road(
    [xodr.Arc(-0.05, angle=np.pi / 2), xodr.Arc(0.05, angle=np.pi / 2)],
    60,
    right_lanes=0,
    left_lanes=1,
)
exit_road2.add_elevation(0, 10, -10 / (40 * np.pi / 2), 0, 0)

entry_road2 = xodr.create_road(
    [xodr.Arc(0.05, angle=np.pi / 2), xodr.Arc(-0.05, angle=np.pi / 2)],
    70,
    left_lanes=0,
    right_lanes=1,
)
entry_road2.add_elevation(0, 10, -10 / (40 * np.pi / 2), 0, 0)

# create the bridge and conneting roads to it
over_road = xodr.create_road(xodr.Line(12), 30, left_lanes=1, right_lanes=1)
over_road.add_elevation(0, 10, 0, 0, 0)

right_road = xodr.create_road(xodr.Line(100), 40, left_lanes=1, right_lanes=1)
right_road.add_elevation(0, 10, 0, 0, 0)

left_road = xodr.create_road(xodr.Line(100), 50, left_lanes=1, right_lanes=1)
left_road.add_elevation(0, 10, 0, 0, 0)

# add the the roads to the right junction

junction_creator_right.add_incoming_road_cartesian_geometry(
    exit_road1, 0, 0, 0, "predecessor"
)
junction_creator_right.add_incoming_road_cartesian_geometry(
    over_road, 30, 40, -np.pi / 2, "predecessor"
)
junction_creator_right.add_incoming_road_cartesian_geometry(
    right_road, 30, -40, 1.001 * np.pi / 2, "predecessor"
)
junction_creator_right.add_incoming_road_cartesian_geometry(
    entry_road2, 60, 0, -np.pi, "predecessor"
)

# add connections and elevations to the created roads

junction_creator_right.add_connection(10, 30)
junction_creator_right.get_connecting_roads()[-1].add_elevation(0, 10, 0, 0, 0)
junction_creator_right.add_connection(40, 30)
junction_creator_right.get_connecting_roads()[-1].add_elevation(0, 10, 0, 0, 0)
junction_creator_right.add_connection(10, 40)
junction_creator_right.get_connecting_roads()[-1].add_elevation(0, 10, 0, 0, 0)
junction_creator_right.add_connection(30, 70)
junction_creator_right.get_connecting_roads()[-1].add_elevation(0, 10, 0, 0, 0)
junction_creator_right.add_connection(40, 70)
junction_creator_right.get_connecting_roads()[-1].add_elevation(0, 10, 0, 0, 0)

# add the roads to the left junction

junction_creator_left.add_incoming_road_cartesian_geometry(
    entry_road1, 0, 0, 0, "successor"
)
junction_creator_left.add_incoming_road_cartesian_geometry(
    over_road, 30, -40, np.pi / 2, "successor"
)
junction_creator_left.add_incoming_road_cartesian_geometry(
    left_road, 30, 40, -1.001 * np.pi / 2, "successor"
)
junction_creator_left.add_incoming_road_cartesian_geometry(
    exit_road2, 60, 0, -np.pi, "predecessor"
)

# add connections and elevations to the created roads

junction_creator_left.add_connection(20, 30)
junction_creator_left.get_connecting_roads()[-1].add_elevation(0, 10, 0, 0, 0)
junction_creator_left.add_connection(20, 50)
junction_creator_left.get_connecting_roads()[-1].add_elevation(0, 10, 0, 0, 0)
junction_creator_left.add_connection(30, 50)
junction_creator_left.get_connecting_roads()[-1].add_elevation(0, 10, 0, 0, 0)
junction_creator_left.add_connection(30, 60)
junction_creator_left.get_connecting_roads()[-1].add_elevation(0, 10, 0, 0, 0)
junction_creator_left.add_connection(60, 50)
junction_creator_left.get_connecting_roads()[-1].add_elevation(0, 10, 0, 0, 0)

# add successors/predecessors to the first direct junction

road_highway_1.add_successor(xodr.ElementType.junction, 300)
road_highway_2.add_predecessor(xodr.ElementType.junction, 300)
exit_road1.add_successor(xodr.ElementType.junction, 300)
entry_road1.add_predecessor(xodr.ElementType.junction, 300)

# add the connections in the first direct junction

junction_creator_direct_first.add_connection(road_highway_1, road_highway_2)
junction_creator_direct_first.add_connection(road_highway_1, exit_road1, -3, 1)
junction_creator_direct_first.add_connection(road_highway_1, entry_road1, 3, 1)

# add successors/predecessors to the second direct junction

road_highway_2.add_successor(xodr.ElementType.junction, 400)
road_highway_3.add_predecessor(xodr.ElementType.junction, 400)
entry_road2.add_successor(xodr.ElementType.junction, 400)
exit_road2.add_successor(xodr.ElementType.junction, 400)

# add the connections in the second direct junction

junction_creator_direct_second.add_connection(road_highway_2, road_highway_3)
junction_creator_direct_second.add_connection(entry_road2, road_highway_3, -1, -3)
junction_creator_direct_second.add_connection(road_highway_3, exit_road2, 3, 1)

# add all the roads
odr = xodr.OpenDrive("highway bridge")
odr.add_road(road_highway_1)
odr.add_road(road_highway_2)
odr.add_road(road_highway_3)
odr.add_road(exit_road1)
odr.add_road(entry_road1)
odr.add_road(over_road)
odr.add_road(right_road)
odr.add_road(left_road)
odr.add_road(entry_road2)
odr.add_road(exit_road2)

# add the junction creators

odr.add_junction_creator(junction_creator_direct_first)
odr.add_junction_creator(junction_creator_right)
odr.add_junction_creator(junction_creator_left)
odr.add_junction_creator(junction_creator_direct_second)

# adjust the roads and lanes

odr.adjust_roads_and_lanes()

# write the OpenDRIVE file as xodr using current script name

odr.write_xml(os.path.basename(__file__).replace(".py", ".xodr"))

# uncomment the following lines to display the road using esmini
# from scenariogeneration import esmini
# esmini(odr,os.path.join('esmini'))
