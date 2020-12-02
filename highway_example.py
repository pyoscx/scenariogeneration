import pyodrx 
import os

# create some simple roads
roads= []
# start road
roads.append(pyodrx.create_road([pyodrx.Spiral(-0.004,0.00001,100), pyodrx.Spiral(0.00001,0.005,50), pyodrx.Arc(0.005,50)],id =0,left_lanes=3,right_lanes=4))
# intermittent road
roads.append(pyodrx.create_road([pyodrx.Spiral(0.0001,0.003,65), pyodrx.Spiral(0.003,0.00001,50) ],id =1,left_lanes=3,right_lanes=3))


#exit road
roads.append(pyodrx.create_road(pyodrx.Line(50),id =2,left_lanes=0,right_lanes=1))
# junctions for exit
roads.append(pyodrx.create_road(pyodrx.Spiral(0.005,0.0001,50),id =3,left_lanes=3,right_lanes=3,road_type=1)) # continue
roads.append(pyodrx.create_road(pyodrx.Spiral(0.005,-0.02,100),id =4,left_lanes=0,right_lanes=1,road_type=1)) # exit

# final road
roads.append(pyodrx.create_road([pyodrx.Spiral(-0.00001,-0.003,45),pyodrx.Arc(-0.003,60)],id =5,left_lanes=2,right_lanes=3))

# entry junction
roads.append(pyodrx.create_road([pyodrx.Line(30) ],id =6,left_lanes=2,right_lanes=3,road_type=2)) # continue
roads.append(pyodrx.create_road([pyodrx.Spiral(0.004,0.000001,50) ],id =7,left_lanes=1,right_lanes=0,road_type=2)) # entry

# entry road
roads.append(pyodrx.create_road(pyodrx.Arc(0.004,60),id =8,left_lanes=1,right_lanes=0))


# add predecessors and succesors to the non junction roads
roads[0].add_successor(pyodrx.ElementType.junction,1)
roads[1].add_predecessor(pyodrx.ElementType.junction,1)
roads[1].add_successor(pyodrx.ElementType.junction,2)
roads[2].add_predecessor(pyodrx.ElementType.junction,1)

# add connections to the first junction road
roads[3].add_predecessor(pyodrx.ElementType.road,0,pyodrx.ContactPoint.end)
roads[3].add_successor(pyodrx.ElementType.road,1,pyodrx.ContactPoint.start)

# add connections to the second junction road, the exit
roads[4].add_predecessor(pyodrx.ElementType.road,0,pyodrx.ContactPoint.end,lane_offset=-3)
roads[4].add_successor(pyodrx.ElementType.road,2,pyodrx.ContactPoint.start)

# add connections to the final road
roads[5].add_predecessor(pyodrx.ElementType.junction,2)

# add connections to the junctionroad that continues
roads[6].add_predecessor(pyodrx.ElementType.road,1,pyodrx.ContactPoint.end)
roads[6].add_successor(pyodrx.ElementType.road,5,pyodrx.ContactPoint.start)

# add connections to the entry junction road
roads[7].add_predecessor(pyodrx.ElementType.road,1,pyodrx.ContactPoint.end,lane_offset=2)
roads[7].add_successor(pyodrx.ElementType.road,8,pyodrx.ContactPoint.start)

# add connection to the entry road
roads[8].add_predecessor(pyodrx.ElementType.junction,2)

# create the junction struct 
exit_junction = pyodrx.create_junction(roads[3:5],1,roads[0:3])
entry_junction = pyodrx.create_junction(roads[6:8],2,[roads[x] for x in [1,5,8]])
# create the opendrive
odr = pyodrx.OpenDrive('myroad')
for r in roads:
    odr.add_road(r)
odr.adjust_roads_and_lanes()
odr.add_junction(exit_junction)
odr.add_junction(entry_junction)

# display the road using esmini
pyodrx.run_road(odr,os.path.join('..','..','esmini'))