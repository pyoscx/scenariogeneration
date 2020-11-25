import pyodrx 
import numpy as np
import os

## EXAMPLE 1 
## Multiple geometries in one only road. 

##1. Create the planview 
planview = pyodrx.PlanView()

##2. Create some geometries and add them to the planview
line1 = pyodrx.Line(100)
arc1 = pyodrx.Arc(0.05,angle=np.pi/2)
line2 = pyodrx.Line(100)
cloth1 = pyodrx.Spiral(0.05,-0.1,30)
line3 = pyodrx.Line(100)

planview.add_geometry(line1)
planview.add_geometry(arc1)
planview.add_geometry(line2)
planview.add_geometry(cloth1)
planview.add_geometry(line3)


##3. Create a solid roadmark
rm = pyodrx.RoadMark(pyodrx.RoadMarkType.solid,0.2,rule=pyodrx.MarkRule.no_passing)

##4. Create centerlane 
centerlane = pyodrx.Lane(a=2)
centerlane.add_roadmark(rm)

##5. Create lane section form the centerlane
lanesec = pyodrx.LaneSection(0,centerlane)

##6. Create left and right lanes
lane2 = pyodrx.Lane(a=3)
lane2.add_roadmark(rm)
lane3 = pyodrx.Lane(a=3)
lane3.add_roadmark(rm)

##7. Add lanes to lane section 
lanesec.add_left_lane(lane2)
lanesec.add_right_lane(lane3)

##8. Add lane section to Lanes 
lanes = pyodrx.Lanes()
lanes.add_lanesection(lanesec)

##9. Create Road from Planview and Lanes
road = pyodrx.Road(1,planview,lanes)

##10. Create the OpenDrive class (Master class)
odr = pyodrx.OpenDrive('myroad')

##11. Finally add roads to Opendrive 
odr.add_road(road)

##12. Adjust initial positions of the roads looking at succ-pred logic 
odr.adjust_roads_and_lanes()

##13. Print the .xodr file
pyodrx.prettyprint(odr.get_element())

##13. Run the .xodr with esmini 
pyodrx.run_road(odr,os.path.join('..','pyoscx','esmini'))

