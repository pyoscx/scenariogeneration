from scenariogeneration import xodr, prettyprint, ScenarioGenerator
import numpy as np
import os


class Scenario(ScenarioGenerator):
    def __init__(self):
        super().__init__()

    def road(self, **kwargs):
        ## create some roads
        start_road = xodr.create_road(
            xodr.Line(50), 0, left_lanes=3, right_lanes=3, lane_width=3
        )
        main_road = xodr.create_road(
            xodr.Spiral(0.00001, 0.01, 50),
            1,
            left_lanes=3,
            right_lanes=3,
            lane_width=3,
        )
        suc_road = xodr.create_road(
            xodr.Line(50), 2, left_lanes=2, right_lanes=2, lane_width=3
        )
        offramp1 = xodr.create_road(
            xodr.Arc(-0.01, 50), 3, left_lanes=0, right_lanes=1, lane_width=3
        )
        offramp2 = xodr.create_road(
            xodr.Arc(0.01, 50), 4, left_lanes=1, right_lanes=0, lane_width=3
        )
        continuation1 = xodr.create_road(
            xodr.Line(50), 5, left_lanes=0, right_lanes=1, lane_width=3
        )
        continuation2 = xodr.create_road(
            xodr.Line(50), 6, left_lanes=1, right_lanes=0, lane_width=3
        )

        ## add some known elevations
        suc_road.add_superelevation(0, 0, 0.002, 0, 0)
        suc_road.add_elevation(0, 10, 0, 0, 0)

        start_road.add_elevation(0, 0, 0.01, 0, 0)
        start_road.add_superelevation(0, 0, 0.0, 0, 0)

        continuation1.add_superelevation(0, 0, 0, 0, 0)
        continuation1.add_elevation(0, 8, 0, 0, 0)

        continuation2.add_superelevation(0, 0, 0, 0, 0)
        continuation2.add_elevation(0, 6, 0, 0, 0)

        ## add successors and predecessors
        start_road.add_successor(
            xodr.ElementType.road, 1, xodr.ContactPoint.start
        )
        main_road.add_predecessor(
            xodr.ElementType.road, 0, xodr.ContactPoint.end
        )
        main_road.add_successor(xodr.ElementType.junction, 100)
        suc_road.add_successor(xodr.ElementType.junction, 100)
        offramp1.add_predecessor(xodr.ElementType.junction, 100)
        offramp2.add_predecessor(xodr.ElementType.junction, 100)
        offramp1.add_successor(
            xodr.ElementType.road, 5, xodr.ContactPoint.start
        )
        offramp2.add_successor(
            xodr.ElementType.road, 6, xodr.ContactPoint.start
        )
        continuation1.add_predecessor(
            xodr.ElementType.road, 3, xodr.ContactPoint.end
        )
        continuation2.add_predecessor(
            xodr.ElementType.road, 4, xodr.ContactPoint.end
        )

        ## create the direct junction
        jc = xodr.DirectJunctionCreator(100, "my junc")
        jc.add_connection(main_road, suc_road)
        jc.add_connection(main_road, offramp1, -3, -1)
        jc.add_connection(main_road, offramp2, 3, 1)

        ## add all roads to the OpenDrive
        odr = xodr.OpenDrive("my_road")
        odr.add_road(start_road)
        odr.add_road(main_road)
        odr.add_road(suc_road)
        odr.add_road(offramp1)
        odr.add_road(offramp2)
        odr.add_road(continuation1)
        odr.add_road(continuation2)

        odr.add_junction_creator(jc)

        # adjust roads and lanes
        odr.adjust_roads_and_lanes()

        # adjust the remaining elevations
        odr.adjust_elevations()

        # adjust the roadmarks
        odr.adjust_roadmarks()

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
