"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2022 The scenariogeneration Authors.

    Example how to create a more customized road with different widths

    Some features used

    - create_road with lane_width_end

"""
from scenariogeneration import xodr, prettyprint, ScenarioGenerator

import os


class Scenario(ScenarioGenerator):
    def __init__(self):
        super().__init__()

    def road(self, **kwargs):
        # create a normal road

        road = xodr.create_road(
            xodr.Line(200),
            id=0,
            left_lanes=3,
            right_lanes=5,
            lane_width=3,
            lane_width_end=9,
        )

        # create the opendrive
        odr = xodr.OpenDrive("myroad")

        odr.add_road(road)
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
