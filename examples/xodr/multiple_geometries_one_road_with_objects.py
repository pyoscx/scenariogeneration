import pyodrx 
import numpy as np
import os
## EXAMPLE 1 
## Multiple geometries in one only road. Additionally adding objects.

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
rm = pyodrx.RoadMark(pyodrx.RoadMarkType.solid,0.2)

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

##13. After adjustment, repeating objects on side of the road can be added automatically
guardrail = pyodrx.Object(0,0,height=0.3,zOffset=0.4,Type=pyodrx.ObjectType.barrier,name="guardRail")
road.add_object_roadside(guardrail, 0, 0, tOffset = 0.8)

delineator = pyodrx.Object(0,0,height=1,zOffset=0,Type=pyodrx.ObjectType.pole,name="delineator")
road.add_object_roadside(delineator, 50, sOffset = 25, tOffset = 0.85)

##14. Add some other objects at specific positions
#single emergency callbox
emergencyCallbox = pyodrx.Object(30,-6,Type=pyodrx.ObjectType.pole,name="emergencyCallBox")
road.add_object(emergencyCallbox)

#repeating jersey barrier
jerseyBarrier = pyodrx.Object(0,0,height=0.75,zOffset=0,Type=pyodrx.ObjectType.barrier,name="jerseyBarrier")
jerseyBarrier.repeat(repeatLength=25,repeatDistance=0,sStart=240)
road.add_object(jerseyBarrier)

##15. Print the .xodr file
pyodrx.prettyprint(odr.get_element())

# write the OpenDRIVE file as xodr using current script name
odr.write_xml(os.path.basename(__file__).replace('.py','.xodr'))

# uncomment the following line to display the road using esmini
# pyodrx.run_road(odr,os.path.join('..','..','esmini'))