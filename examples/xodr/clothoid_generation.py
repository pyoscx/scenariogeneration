"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2023 The scenariogeneration Authors.

    Example how to utilze pyclothoids to create a road to match two points


    Some features used:

    - create_road

    - pyclothoids* (external package)

"""


from scenariogeneration import xodr, prettyprint, ScenarioGenerator

import pyclothoids as pcloth
import os


class Scenario(ScenarioGenerator):
    def __init__(self):
        super().__init__()

    def road(self, **kwargs):
        start_x = 0  # x coordinate at the beginning of the curvature
        start_y = 0  # y coordinate at the beginning of the curvature
        start_h = 0  # heading at the beginning of the curvature

        end_x = 150  # x coordinate at the end of the curvature
        end_y = 20  # y coordinate at the end of the curvature
        end_h = 0  # heading at the end of the curvature

        clothoids = pcloth.SolveG2(
            start_x,
            start_y,
            start_h,
            xodr.STD_START_CLOTH,
            end_x,
            end_y,
            end_h,
            xodr.STD_START_CLOTH,
        )
        # create spirals from each responce
        roadgeoms = [
            xodr.Spiral(x.KappaStart, x.KappaEnd, length=x.length) for x in clothoids
        ]

        # create the road
        road = xodr.create_road(roadgeoms, id=0, left_lanes=2, right_lanes=2)

        ## Create the OpenDrive class (Master class)
        odr = xodr.OpenDrive("myroad")

        ## Finally add roads to Opendrive
        odr.add_road(road)

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
