import pyodrx 

import os

# create some roads 
roads= []
roads.append(pyodrx.create_road(pyodrx.Line(100),id = 0, left_lanes=1,right_lanes=2))
roads.append(pyodrx.create_road(pyodrx.Line(100),id =1,left_lanes=0,right_lanes=1))
roads.append(pyodrx.create_road(pyodrx.Line(100),id =2,left_lanes=1,right_lanes=3))
roads.append(pyodrx.create_road(pyodrx.Spiral(0.001,0.02,30),id =3,left_lanes=1,right_lanes=2,road_type=1))
roads.append(pyodrx.create_road(pyodrx.Spiral(-0.001,-0.02,30),id =4,left_lanes=0,right_lanes=1,road_type=1))

# add some connections to non junction roads
roads[0].add_successor(pyodrx.ElementType.junction,1)
roads[1].add_successor(pyodrx.ElementType.junction,1)
roads[2].add_predecessor(pyodrx.ElementType.junction,1)

# add connections to the first connecting road
roads[3].add_predecessor(pyodrx.ElementType.road,0,pyodrx.ContactPoint.end)
roads[3].add_successor(pyodrx.ElementType.road,2,pyodrx.ContactPoint.start)

# add connections to the second connecting road with an offset
roads[4].add_predecessor(pyodrx.ElementType.road,1,pyodrx.ContactPoint.end)
roads[4].add_successor(pyodrx.ElementType.road,2,pyodrx.ContactPoint.start,lane_offset=-2)


  
junction = pyodrx.create_junction(roads[3:],1,roads[0:3])


# create the opendrive
odr = pyodrx.OpenDrive('myroad')
for r in roads:
    odr.add_road(r)
odr.adjust_roads_and_lanes()
odr.add_junction(junction)
pyodrx.run_road(odr,os.path.join('..','..','esmini'))

