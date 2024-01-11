"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2022 The scenariogeneration Authors.

    Example how to create a more customized junction with different widths of lanes, using basic classes

    Some features used

    - CommonJunctionCreator

    - Lane
"""
from scenariogeneration import xodr, prettyprint, ScenarioGenerator
import numpy as np

import os


class Scenario(ScenarioGenerator):
    def __init__(self):
        super().__init__()

    def road(self, **kwargs):
        # create road_1
        road_1_geo = xodr.Line(60.0)
        road_1_pv = xodr.PlanView(x_start=0.0, y_start=0.0, h_start=0.0)
        road_1_pv.add_geometry(road_1_geo)

        road_1_left_lane_1 = xodr.Lane(a=4.0)
        road_1_right_lane_1 = xodr.Lane(a=2.0)
        road_1_right_lane_2 = xodr.Lane(a=4.0)
        road_1_center_lane = xodr.Lane()

        road_1_lane_section = xodr.LaneSection(0.0, road_1_center_lane)
        road_1_lane_section.add_left_lane(road_1_left_lane_1)
        road_1_lane_section.add_right_lane(road_1_right_lane_1)
        road_1_lane_section.add_right_lane(road_1_right_lane_2)

        road_1_lanes = xodr.Lanes()
        road_1_lanes.add_lanesection(road_1_lane_section)

        road_1 = xodr.Road(road_id=1, planview=road_1_pv, lanes=road_1_lanes)

        # create road_2
        road_2_geo = xodr.Line(60.0)
        road_2_pv = xodr.PlanView(x_start=100.0, y_start=-40.0, h_start=-np.pi / 2)
        road_2_pv.add_geometry(road_2_geo)

        road_2_left_lane_1 = xodr.Lane(a=1.0)
        road_2_right_lane_1 = xodr.Lane(a=5.0)
        road_2_right_lane_2 = xodr.Lane(a=8.0)
        road_2_center_lane = xodr.Lane()

        road_2_lane_section = xodr.LaneSection(0.0, road_2_center_lane)
        road_2_lane_section.add_left_lane(road_2_left_lane_1)
        road_2_lane_section.add_right_lane(road_2_right_lane_1)
        road_2_lane_section.add_right_lane(road_2_right_lane_2)

        road_2_lanes = xodr.Lanes()
        road_2_lanes.add_lanesection(road_2_lane_section)

        road_2 = xodr.Road(road_id=2, planview=road_2_pv, lanes=road_2_lanes)

        # add the roads to odr class
        odr = xodr.OpenDrive("myroad")
        odr.add_road(road_1)
        odr.add_road(road_2)

        # create junction
        junction_creator = xodr.CommonJunctionCreator(
            id=1,
            name="junction_1",
            startnum=3,
        )
        junction_creator.add_incoming_road_cartesian_geometry(
            road_1, x=0.0, y=0.0, heading=0.0, road_connection="successor"
        )
        junction_creator.add_incoming_road_cartesian_geometry(
            road_2,
            x=40.0,
            y=-40.0,
            heading=np.pi / 2,
            road_connection="predecessor",
        )
        # create connections
        junction_creator.add_connection(
            road_one_id=1, road_two_id=2, lane_one_id=1, lane_two_id=1
        )
        junction_creator.add_connection(
            road_one_id=1, road_two_id=2, lane_one_id=-1, lane_two_id=-1
        )
        junction_creator.add_connection(
            road_one_id=1, road_two_id=2, lane_one_id=-2, lane_two_id=-2
        )
        # add the junction creator
        odr.add_junction_creator(junction_creator)
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
