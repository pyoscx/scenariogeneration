import pyodrx 
import os

# create some simple roads
roads= []

# create the planview and the geometry
planview = pyodrx.PlanView()
planview.add_geometry(pyodrx.Line(200))


# create two different roadmarkings
rm_solid = pyodrx.RoadMark(pyodrx.RoadMarkType.solid,0.2,rule=pyodrx.MarkRule.no_passing)
rm_dashed = pyodrx.RoadMark(pyodrx.RoadMarkType.broken,0.2,rule=pyodrx.MarkRule.no_passing)


# create a centerlane (same centerlane can be used since no linking is needed for this)
centerlane = pyodrx.Lane(a=2)
centerlane.add_roadmark(rm_solid)

# create first lanesection with two lanes
lanesec1 = pyodrx.LaneSection(0,centerlane)
lane0 = pyodrx.Lane(a=3)
lane0.add_roadmark(rm_dashed)
lane1 = pyodrx.Lane(a=3)
lane1.add_roadmark(rm_solid)

lanesec1.add_right_lane(lane0)
lanesec1.add_right_lane(lane1)

# create the second lanesection with a third lane emerging
lanesec2 = pyodrx.LaneSection(100,centerlane)
lane2 = pyodrx.Lane(a=3)
lane2.add_roadmark(rm_dashed)

lane3 = pyodrx.Lane(a=3)
lane3.add_roadmark(rm_dashed)

lane4 = pyodrx.Lane(a=0,b=0.1)
lane4.add_roadmark(rm_solid)

lanesec2.add_right_lane(lane2)
lanesec2.add_right_lane(lane3)
lanesec2.add_right_lane(lane4)

# create the last lanesection with two paralell lanes
lanesec3 = pyodrx.LaneSection(130,centerlane)
lane5 = pyodrx.Lane(a=3)
lane5.add_roadmark(rm_dashed)

lane6 = pyodrx.Lane(a=3)
lane6.add_roadmark(rm_dashed)

lane7 = pyodrx.Lane(a=3)
lane7.add_roadmark(rm_solid)

lanesec3.add_right_lane(lane5)
lanesec3.add_right_lane(lane6)
lanesec3.add_right_lane(lane7)

# create the lane links
lanelinker = pyodrx.LaneLinker()
lanelinker.add_link(predlane=lane0,succlane=lane2)
lanelinker.add_link(predlane=lane1,succlane=lane3)
lanelinker.add_link(predlane=lane2,succlane=lane5)
lanelinker.add_link(predlane=lane3,succlane=lane6)
lanelinker.add_link(predlane=lane4,succlane=lane7)

# create the lanes with the correct links
lanes = pyodrx.Lanes()
lanes.add_lanesection(lanesec1,lanelinker)
lanes.add_lanesection(lanesec2,lanelinker)
lanes.add_lanesection(lanesec3,lanelinker)

# create the road
roads.append(pyodrx.Road(0,planview,lanes))

# create the other roads
roads.append(pyodrx.create_road(pyodrx.Line(100),id =1,left_lanes=0,right_lanes=2))
roads.append(pyodrx.create_road(pyodrx.Line(100),id =2,left_lanes=0,right_lanes=1))
# create the junction roads
roads.append(pyodrx.create_road(pyodrx.Spiral(0.001,0.02,30),id =3,left_lanes=0,right_lanes=2,road_type=1))
roads.append(pyodrx.create_road(pyodrx.Spiral(-0.001,-0.02,30),id =4,left_lanes=0,right_lanes=1,road_type=1))

# add predecessors and succesors to the non junction roads
roads[0].add_successor(pyodrx.ElementType.junction,1)
roads[1].add_predecessor(pyodrx.ElementType.junction,1)
roads[2].add_predecessor(pyodrx.ElementType.junction,1)

# add connections to the first junction road
roads[3].add_predecessor(pyodrx.ElementType.road,0,pyodrx.ContactPoint.end)
roads[3].add_successor(pyodrx.ElementType.road,1,pyodrx.ContactPoint.start)

# add connections to the second junction road, together with an offset
roads[4].add_predecessor(pyodrx.ElementType.road,0,pyodrx.ContactPoint.end,lane_offset=-2)
roads[4].add_successor(pyodrx.ElementType.road,2,pyodrx.ContactPoint.start)

# create the junction struct 
junction = pyodrx.create_junction(roads[3:],1,roads[0:3])

# create the opendrive
odr = pyodrx.OpenDrive('myroad')
for r in roads:
    odr.add_road(r)
odr.adjust_roads_and_lanes()
odr.add_junction(junction)


# display the road using esmini
pyodrx.run_road(odr,os.path.join('..','..','esmini'))