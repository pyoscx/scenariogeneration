"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2023 The scenariogeneration Authors.

    Example how to utilze AdjustablePlanview to make a loop with to difficult geometries to manually calculate


    Some features used:

    - AdjustablePlanview

    - CommonJunctionCreator

"""


from scenariogeneration import xodr, prettyprint, ScenarioGenerator


class Scenario(ScenarioGenerator):
    def __init__(self):
        super().__init__()

    def road(self, **kwargs):
        ## create 3 roads
        road1 = xodr.create_road(
            [xodr.Line(30), xodr.Spiral(-0.00001, -0.035, 200)], 1, 2, 2
        )
        road2 = xodr.create_road(xodr.Line(100), 2, 2, 2)
        road3 = xodr.create_road(xodr.Line(100), 3, 2, 2)

        ## make a common junction

        jc = xodr.CommonJunctionCreator(100, "my junc")

        jc.add_incoming_road_cartesian_geometry(road1, 0, 0, 0, "successor")
        jc.add_incoming_road_cartesian_geometry(road2, 30, 0, -3.14, "predecessor")
        jc.add_incoming_road_cartesian_geometry(road3, 15, 15, -3.14 / 2, "successor")

        jc.add_connection(1, 2)
        jc.add_connection(3, 2)
        jc.add_connection(3, 1)

        ## make a forth road to connect two of the roads connected to the junction
        # since road1 has a Spiral as one geometry, it is very hard to determine the geometry of road4
        # instead use AdjustablePlanview as geometry!
        road4 = xodr.create_road(xodr.AdjustablePlanview(100), 4, 2, 2)

        # add predecessors and successors to the roads
        road4.add_predecessor(xodr.ElementType.road, 2, xodr.ContactPoint.end)
        road4.add_successor(xodr.ElementType.road, 1, xodr.ContactPoint.start)

        road2.add_successor(xodr.ElementType.road, 4, xodr.ContactPoint.start)
        road1.add_predecessor(xodr.ElementType.road, 4, xodr.ContactPoint.end)

        ## add roads to OpenDrive
        odr = xodr.OpenDrive("my road")
        odr.add_road(road1)
        odr.add_road(road2)
        odr.add_road(road3)
        odr.add_road(road4)
        odr.add_junction_creator(jc)

        ## Adjust initial positions of the roads looking at succ-pred logic
        odr.adjust_roads_and_lanes()

        return odr


if __name__ == "__main__":
    sce = Scenario()
    # Print the resulting xml
    prettyprint(sce.road().get_element())

    # write the OpenDRIVE file as xosc using current script name
    sce.generate(".")

    # uncomment the following lines to display the scenario using esmini
    # from scenariogeneration import esmini
    # esmini(sce,os.path.join('esmini'))
