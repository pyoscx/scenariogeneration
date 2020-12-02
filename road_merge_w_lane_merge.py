import pyodrx 

import os

# create some roads 
roads= []

# create two simple roads to merge
roads.append(pyodrx.create_road(pyodrx.Line(100),id = 0, left_lanes=0,right_lanes=2))
roads.append(pyodrx.create_road(pyodrx.Line(100),id =1,left_lanes=0,right_lanes=1))

# manually create the final road


# create the planview and the geometry
planview = pyodrx.PlanView()
planview.add_geometry(pyodrx.Line(200))

# create two different roadmarkings
rm_solid = pyodrx.RoadMark(pyodrx.RoadMarkType.solid,0.2,rule=pyodrx.MarkRule.no_passing)
rm_dashed = pyodrx.RoadMark(pyodrx.RoadMarkType.broken,0.2,rule=pyodrx.MarkRule.no_passing)

# create a centerlane (same centerlane can be used since no linking is needed for this)
centerlane = pyodrx.Lane(a=2)
centerlane.add_roadmark(rm_solid)

# create the first lanesection with three lanes
lanesec1 = pyodrx.LaneSection(0,centerlane)
lane1 = pyodrx.Lane(a=3)
lane1.add_roadmark(rm_dashed)

lane2 = pyodrx.Lane(a=3)
lane2.add_roadmark(rm_dashed)

lane3 = pyodrx.Lane(a=3)
lane3.add_roadmark(rm_solid)

lanesec1.add_right_lane(lane1)
lanesec1.add_right_lane(lane2)
lanesec1.add_right_lane(lane3)

# create the second lanesection with one lane merging
lanesec2 = pyodrx.LaneSection(70,centerlane)
lane4 = pyodrx.Lane(a=3)
lane4.add_roadmark(rm_dashed)

lane5 = pyodrx.Lane(a=3)
lane5.add_roadmark(rm_dashed)

lane6 = pyodrx.Lane(a=3,b=-0.1)
lane6.add_roadmark(rm_solid)

lanesec2.add_right_lane(lane4)
lanesec2.add_right_lane(lane5)
lanesec2.add_right_lane(lane6)

# create the last lanesection with one lane
lanesec3 = pyodrx.LaneSection(100,centerlane)

lane7 = pyodrx.Lane(a=3)
lane7.add_roadmark(rm_dashed)

lane8 = pyodrx.Lane(a=3)
lane8.add_roadmark(rm_solid)

lanesec3.add_right_lane(lane7)
lanesec3.add_right_lane(lane8)

# create the lane links
lanelinker = pyodrx.LaneLinker()
lanelinker.add_link(predlane=lane1,succlane=lane4)
lanelinker.add_link(predlane=lane2,succlane=lane5)
lanelinker.add_link(predlane=lane3,succlane=lane6)

lanelinker.add_link(predlane=lane5,succlane=lane7)
lanelinker.add_link(predlane=lane6,succlane=lane8)

# create the lanes with the correct links
lanes = pyodrx.Lanes()
lanes.add_lanesection(lanesec1,lanelinker)
lanes.add_lanesection(lanesec2,lanelinker)
lanes.add_lanesection(lanesec3,lanelinker)

# create the road
roads.append(pyodrx.Road(2,planview,lanes))


# create junction roads
roads.append(pyodrx.create_road(pyodrx.Spiral(0.001,0.02,30),id =3,left_lanes=0,right_lanes=2,road_type=1))
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

