"""
    Example of how to create a highway exit on both sides using a direct junction.
"""
from scenariogeneration import xodr
import os

# create some simple roads
roads= []

exit_road_left = xodr.create_road(xodr.Spiral(0,0.01,length=50),1,left_lanes = 1,right_lanes=0)
continuation_road_in = xodr.create_road(xodr.Line(100),2,left_lanes = 1,right_lanes=2)
continuation_road_out = xodr.create_road(xodr.Line(100),3,left_lanes=2,right_lanes=1)
exit_road_right = xodr.create_road(xodr.Spiral(0,-0.01,length=50),4,left_lanes = 0, right_lanes = 1)

# add successors and predecessors as a direct junction
exit_road_left.add_successor(xodr.ElementType.junction,100,lane_offsets=[1],direct_junction=[3])
continuation_road_in.add_successor(xodr.ElementType.junction,100,lane_offsets=[0,1],direct_junction=[3,4])
continuation_road_out.add_predecessor(xodr.ElementType.junction,100,lane_offsets=[-1,0],direct_junction=[1,2])
exit_road_right.add_predecessor(xodr.ElementType.junction,100,lane_offsets=[-1],direct_junction=[2])

# create the junction struct
direct_junction = xodr.create_direct_junction([exit_road_left,continuation_road_in,continuation_road_out,exit_road_right],100)

# create the opendrive
odr = xodr.OpenDrive('myroads')

# first road needs to be fixed in order to place it correctly
odr.add_road(continuation_road_in)
odr.add_road(exit_road_left)
odr.add_road(continuation_road_out)
odr.add_road(exit_road_right)

# adjust the roads and lanes properly
odr.adjust_roads_and_lanes()
odr.add_junction(direct_junction)

# write the OpenDRIVE file as xodr using current script name
odr.write_xml(os.path.basename(__file__).replace('.py','.xodr'))
