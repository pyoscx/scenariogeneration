import pyodrx 
import numpy as np
import os



planview = pyodrx.PlanView()

# create some geometries and add to the planview
line1 = pyodrx.Line(100)
planview.add_geometry(line1)



arc1 = pyodrx.Arc(0.05,angle=np.pi/2)
planview.add_geometry(arc1)


line2 = pyodrx.Line(100)
planview.add_geometry(line2)

arc2 = pyodrx.Arc(-0.05,angle=np.pi/2)
planview.add_geometry(arc2)



# create a solid roadmark
rm = pyodrx.RoadMark(pyodrx.RoadMarkType.solid,0.2,rule=pyodrx.MarkRule.no_passing)

# create centerlane
centerlane = pyodrx.Lane(a=2)
centerlane.add_roadmark(rm)
lanesec = pyodrx.LaneSection(0,centerlane)


# add a driving lane
lane2 = pyodrx.Lane(a=3)
lane2.add_roadmark(rm)

lanesec.add_left_lane(lane2)

lane3 = pyodrx.Lane(a=3)
lane3.add_roadmark(rm)

lanesec.add_right_lane(lane3)

## finalize the road
lanes = pyodrx.Lanes()
lanes.add_lanesection(lanesec)




road = pyodrx.Road(1,planview,lanes)

odr = pyodrx.OpenDrive('myroad')

odr.add_road(road)
odr.adjust_roads_and_lanes()
pyodrx.prettyprint(odr.get_element())

pyodrx.run_road(odr,os.path.join('..','pyoscx','esmini'))

