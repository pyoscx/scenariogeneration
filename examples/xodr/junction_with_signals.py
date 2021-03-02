# Same approach to creating a junction as "full_junction.py" but with signals for each incoming road.
import numpy as np
import os
import pyodrx
#import pyoscx

roads = []
incoming_roads = 4
angles = []
for i in range(incoming_roads):
    roads.append(pyodrx.create_straight_road(i))
    # use this instead to change the number of lanes in the crossing
    # roads.append(pyodrx.generators.create_straight_road(i, length=100, junction=-1, n_lanes=2, lane_offset=3))
    angles.append(i * 2 * np.pi / incoming_roads)
    if angles[-1] == 0:
        roads[-1].add_signal(pyodrx.Signal(s=98.0, t=-4, country="USA", Type="R1", subtype="1"))
    else:
        roads[-1].add_signal(pyodrx.Signal(s=2.0, t=4, country="USA", Type="R1", subtype="1", orientation=pyodrx.Orientation.negative))

        

# use this for a T-crossing instead
# angles = [0,np.pi/2, 3*np.pi/2]

print(roads)
junc = pyodrx.create_junction_roads(roads, angles, 8)
odr = pyodrx.OpenDrive('myroad')
junction = pyodrx.create_junction(junc, 1, roads)

odr.add_junction(junction)
for r in roads:
    odr.add_road(r)
for j in junc:
    odr.add_road(j)

odr.adjust_roads_and_lanes()

# write the OpenDRIVE file as xodr using current script name
odr.write_xml(os.path.basename(__file__).replace('.py','.xodr'))

# uncomment the following line to display the road using esmini
# pyodrx.run_road(odr,os.path.join('..','..','esmini'))