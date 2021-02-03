import pyodrx 
import numpy as np
import os


odr = pyodrx.OpenDrive('myroad')

#---------------- Road 1
planview = pyodrx.PlanView(0,0,0)

# create some geometries and add to the planview
planview.add_geometry(pyodrx.Line(100))

# create a solid roadmark
rm = pyodrx.RoadMark(pyodrx.RoadMarkType.solid, 0.2)

# create centerlane
centerlane_1 = pyodrx.Lane(a=2)
centerlane_1.add_roadmark(rm)
lanesec_1 = pyodrx.LaneSection(0,centerlane_1)

# add a driving lane
lane2_1 = pyodrx.Lane(a=3.1)
lane2_1.add_roadmark(rm)
lanesec_1.add_left_lane(lane2_1)

lane3_1 = pyodrx.Lane(a=3.1)
lane3_1.add_roadmark(rm)
lanesec_1.add_right_lane(lane3_1)

## finalize the road
lanes_1 = pyodrx.Lanes()
lanes_1.add_lanesection(lanesec_1)

road = pyodrx.Road(1,planview,lanes_1)


odr.add_road(road)


#---------------- Road 2

planview2 = pyodrx.PlanView(x_start = 0, y_start = 10,h_start=np.pi/2)
# planview2 = pyodrx.PlanView()

# create some geometries and add to the planview
planview2.add_geometry(pyodrx.Line(200))

# create a solid roadmark
rm = pyodrx.RoadMark(pyodrx.RoadMarkType.solid, 0.2)

# create centerlane
centerlane = pyodrx.Lane(a=2)
centerlane.add_roadmark(rm)
lanesec = pyodrx.LaneSection(0,centerlane)

# add a driving lane
lane2 = pyodrx.Lane(a=3.1)
lane2.add_roadmark(rm)
lanesec.add_left_lane(lane2)

lane3 = pyodrx.Lane(a=3.1)
lane3.add_roadmark(rm)
lanesec.add_right_lane(lane3)

## finalize the road
lanes = pyodrx.Lanes()
lanes.add_lanesection(lanesec)

road2 = pyodrx.Road(2,planview2,lanes)

odr.add_road(road2)




#------------------ Finalize
odr.adjust_roads_and_lanes()
pyodrx.prettyprint(odr.get_element())

pyodrx.run_road(odr,os.path.join('..','..','esmini'))

