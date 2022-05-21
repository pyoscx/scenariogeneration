"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.
  
    An example, using the generators, showing how to create a highway with exits and entries, that has their own entry and exit lanes

    Shows how to patch created roads together with successor/predecessor, together with the lane_offset option

    Some features used:

    - create_road

    - LaneDef (not a real OpenDrive definition but a helper for the xodr module)

    - add_successor/add_predecessor with and without the lane_offset option

    - create_junction


"""

from scenariogeneration import xodr
import os

# create some simple roads
roads = []
# start road
roads.append(
    xodr.create_road(
        [
            xodr.Spiral(-0.004, 0.00001, 100),
            xodr.Spiral(0.00001, 0.005, 50),
            xodr.Arc(0.005, 50),
        ],
        id=0,
        left_lanes=2,
        right_lanes=[xodr.LaneDef(50, 175, 3, 4, -4)],
    )
)
# intermittent road
roads.append(
    xodr.create_road(
        [xodr.Spiral(0.0001, 0.003, 65), xodr.Spiral(0.003, 0.00001, 50)],
        id=1,
        left_lanes=[xodr.LaneDef(10, 100, 2, 3, 3)],
        right_lanes=3,
    )
)


# exit road
roads.append(xodr.create_road(xodr.Line(50), id=2, left_lanes=0, right_lanes=1))
# junctions for exit
roads.append(
    xodr.create_road(
        xodr.Spiral(0.005, 0.0001, 50), id=3, left_lanes=2, right_lanes=3, road_type=1
    )
)  # continue
roads.append(
    xodr.create_road(
        xodr.Spiral(0.005, -0.02, 100), id=4, left_lanes=0, right_lanes=1, road_type=1
    )
)  # exit

# final road
roads.append(
    xodr.create_road(
        [xodr.Spiral(-0.00001, -0.003, 45), xodr.Arc(-0.003, 60)],
        id=5,
        left_lanes=2,
        right_lanes=3,
    )
)

# entry junction
roads.append(
    xodr.create_road([xodr.Line(30)], id=6, left_lanes=2, right_lanes=3, road_type=2)
)  # continue
roads.append(
    xodr.create_road(
        [xodr.Spiral(0.004, 0.000001, 50)],
        id=7,
        left_lanes=1,
        right_lanes=0,
        road_type=2,
    )
)  # entry

# entry road
roads.append(xodr.create_road(xodr.Arc(0.004, 60), id=8, left_lanes=1, right_lanes=0))


# add predecessors and succesors to the non junction roads
roads[0].add_successor(xodr.ElementType.junction, 1)
roads[1].add_predecessor(xodr.ElementType.junction, 1)
roads[1].add_successor(xodr.ElementType.junction, 2)
roads[2].add_predecessor(xodr.ElementType.junction, 1)

# add connections to the first junction road
roads[3].add_predecessor(xodr.ElementType.road, 0, xodr.ContactPoint.end)
roads[3].add_successor(xodr.ElementType.road, 1, xodr.ContactPoint.start)

# add connections to the second junction road, the exit
roads[4].add_predecessor(
    xodr.ElementType.road, 0, xodr.ContactPoint.end, lane_offset=-3
)
roads[4].add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.start)

# add connections to the final road
roads[5].add_predecessor(xodr.ElementType.junction, 2)

# add connections to the junctionroad that continues
roads[6].add_predecessor(xodr.ElementType.road, 1, xodr.ContactPoint.end)
roads[6].add_successor(xodr.ElementType.road, 5, xodr.ContactPoint.start)

# add connections to the entry junction road
roads[7].add_predecessor(xodr.ElementType.road, 1, xodr.ContactPoint.end, lane_offset=2)
roads[7].add_successor(xodr.ElementType.road, 8, xodr.ContactPoint.start)

# add connection to the entry road
roads[8].add_predecessor(xodr.ElementType.junction, 2)

# create the junction struct
exit_junction = xodr.create_junction(roads[3:5], 1, roads[0:3])
entry_junction = xodr.create_junction(roads[6:8], 2, [roads[x] for x in [1, 5, 8]])
# create the opendrive
odr = xodr.OpenDrive("myroad")
for r in roads:
    odr.add_road(r)
odr.adjust_roads_and_lanes()
odr.add_junction(exit_junction)
odr.add_junction(entry_junction)

# write the OpenDRIVE file as xodr using current script name
odr.write_xml(os.path.basename(__file__).replace(".py", ".xodr"))

# uncomment the following lines to display the road using esmini
# from scenariogeneration import esmini
# esmini(odr,os.path.join('esmini'))
