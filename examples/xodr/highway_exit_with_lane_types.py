"""
    An example, using the generators, showing how to create a simple highway with exits and entries

    Shows how to patch created roads together with successor/predecessor, together with the lane_offset option

    Some features used:

    - create_road

    - add_successor/add_predecessor with and without the lane_offset option

    - LaneDef

    - LaneType

    - create_direct_junction
"""

from scenariogeneration import xodr
import os

# create a road with an exit lane (three lane sections will be created)
first_road = xodr.create_road(xodr.Spiral(0.001,0,300),1,left_lanes = 2,right_lanes=[xodr.LaneDef(100,200,2,3,-3)])

# add the type of lane to the exit and offramp
first_road.lanes.lanesections[1].rightlanes[2].lane_type = xodr.LaneType.exit
first_road.lanes.lanesections[2].rightlanes[2].lane_type = xodr.LaneType.exit

continuation_road = xodr.create_road(xodr.Spiral(0.00001,0.001,200),2,left_lanes=2,right_lanes=2)
exit_road = xodr.create_road([xodr.Spiral(0,-0.01,length=50),xodr.Arc(-0.01,length=30),xodr.Spiral(-0.01,0,length=50)],3,0,1)
exit_road.lanes.lanesections[0].rightlanes[0].lane_type = xodr.LaneType.offRamp

# add successors and predecessors as a direct junction
first_road.add_successor(xodr.ElementType.junction,100,direct_junction=[2,3])
continuation_road.add_predecessor(xodr.ElementType.junction,100,direct_junction=[1])
exit_road.add_predecessor(xodr.ElementType.junction,100,lane_offset=-2,direct_junction=[1])

# create the junction struct
direct_junction = xodr.create_direct_junction([first_road,continuation_road,exit_road],100)

# create the opendrive
odr = xodr.OpenDrive('myroad')
odr.add_road(first_road)
odr.add_road(continuation_road)
odr.add_road(exit_road)

# adjust the roads and lanes properly
odr.adjust_roads_and_lanes()
odr.add_junction(direct_junction)


# write the OpenDRIVE file as xodr using current script name
odr.write_xml(os.path.basename(__file__).replace('.py','.xodr'))

# uncomment the following lines to display the road using esmini
# from scenariogeneration import esmini
# esmini(odr,os.path.join('esmini'))
