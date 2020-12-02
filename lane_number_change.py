import pyodrx
import os


planview = pyodrx.PlanView()


planview.add_geometry(pyodrx.Line(500))



rm_solid = pyodrx.RoadMark(pyodrx.RoadMarkType.solid,0.2,rule=pyodrx.MarkRule.no_passing)
rm_dashed = pyodrx.RoadMark(pyodrx.RoadMarkType.broken,0.2,rule=pyodrx.MarkRule.no_passing)
rm_dashed_offset = pyodrx.RoadMark(pyodrx.RoadMarkType.broken,0.2,rule=pyodrx.MarkRule.no_passing)


centerlane = pyodrx.Lane(a=2)
centerlane.add_roadmark(rm_solid)

lanesec1 = pyodrx.LaneSection(0,centerlane)
lane1 = pyodrx.Lane(a=3)
lane1.add_roadmark(rm_solid)
lanesec1.add_right_lane(lane1)

lanesec2 = pyodrx.LaneSection(250,centerlane)
lane2 = pyodrx.Lane(a=3)
lane3 = pyodrx.Lane(a=0.01,b=0.1)

lane2.add_roadmark(rm_dashed)
lane3.add_roadmark(rm_solid)

lanesec2.add_right_lane(lane2)
lanesec2.add_right_lane(lane3)


lanesec3 = pyodrx.LaneSection(280,centerlane)
lane4 = pyodrx.Lane(a=3)
lane5 = pyodrx.Lane(a=3)

lane4.add_roadmark(rm_dashed)
lane5.add_roadmark(rm_solid)

lanesec3.add_right_lane(lane4)
lanesec3.add_right_lane(lane5)




lanelinker = pyodrx.LaneLinker()
lanelinker.add_link(predlane=lane1,succlane=lane2)
lanelinker.add_link(predlane=lane2,succlane=lane4)
lanelinker.add_link(lane3,lane5)


lanes = pyodrx.Lanes()
lanes.add_lanesection(lanesec1,lanelinker)
lanes.add_lanesection(lanesec2,lanelinker)
lanes.add_lanesection(lanesec3,lanelinker)

road = pyodrx.Road(1,planview,lanes)

odr = pyodrx.OpenDrive('myroad')


odr.add_road(road)


odr.adjust_roads_and_lanes()

pyodrx.run_road(odr,os.path.join('/home/mander76/local/scenario_creation/esmini'))