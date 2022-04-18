"""
    Example of how to create a highway entry using direct junctions.

    Some features used:

    - create_road

    - add_successor/add_predecessor with and without the lane_offset option, and the direct_junction input

    - create_direct_junction
"""
from scenariogeneration import xodr
import os

# create some simple roads
roads = []

first_road = xodr.create_road(xodr.Line(100), 1, left_lanes=3, right_lanes=2)
continuation_road = xodr.create_road(xodr.Line(100), 2, left_lanes=2, right_lanes=2)
entry_road = xodr.create_road(xodr.Line(50), 3, left_lanes=1, right_lanes=0)

# add successors and predecessors as a direct junction
first_road.add_successor(xodr.ElementType.junction, 100, direct_junction=[2, 3])
continuation_road.add_predecessor(xodr.ElementType.junction, 100, direct_junction=[1])
entry_road.add_predecessor(
    xodr.ElementType.junction, 100, lane_offset=2, direct_junction=[1]
)

# create the direct junction struct
direct_junction = xodr.create_direct_junction(
    [first_road, continuation_road, entry_road], 100
)

# create the opendrive
odr = xodr.OpenDrive("myroad")
odr.add_road(first_road)
odr.add_road(continuation_road)
odr.add_road(entry_road)

# adjust the roads and lanes properly
odr.adjust_roads_and_lanes()

odr.add_junction(direct_junction)

# write the OpenDRIVE file as xodr using current script name
odr.write_xml(os.path.basename(__file__).replace(".py", ".xodr"))

# uncomment the following lines to display the road using esmini
from scenariogeneration import esmini
esmini(odr,os.path.join('esmini'))
