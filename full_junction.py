import numpy as np
import os

import pyodrx



    
roads = []
numintersections = 4 # 3 or 4
angles = []
for i in range(numintersections):
    roads.append(pyodrx.create_straight_road(i))
    # use this instead to change the number of lanes in the crossing 
    #roads.append(pyodrx.generators.create_straight_road(i, length=100, junction=-1, n_lanes=2, lane_offset=3))
    angles.append(i * 2*np.pi/numintersections)

# use this for a T-crossing instead
# angles = [0,np.pi/2, 3*np.pi/2]

print(roads)
junc = pyodrx.create_junction_roads(roads,angles,8)

odr = pyodrx.OpenDrive('myroad')
junction = pyodrx.create_junction(junc,1,roads)

odr.add_junction(junction)
for r in roads:
    odr.add_road(r)
for j in junc:
    odr.add_road(j)

odr.adjust_roads_and_lanes()

pyodrx.run_road(odr,os.path.join('..','pyoscx','esmini')) 