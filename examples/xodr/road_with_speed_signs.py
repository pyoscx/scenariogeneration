"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2022 The scenariogeneration Authors.

    Example how to create a more customized a junction with different widths of lanes,
    using generators and LaneDef with different lane widths

    Some features used

    - create_road

    - Signal
"""

from scenariogeneration import xodr, prettyprint, ScenarioGenerator
import numpy as np
import os


class Scenario(ScenarioGenerator):
    def __init__(self):
        super().__init__()

    def road(self, **kwargs):
        # create a road with some strange lane sections
        road1 = xodr.create_road(xodr.Line(200), 1, 3, 3, lane_width=4)

        # create 3 poles
        road1.add_object(
            xodr.Object(
                s=100, t=-12, id=1, length=0.05, width=0.05, radius=0.5, height=2.3
            )
        )
        road1.add_object(
            xodr.Object(
                s=100, t=0, id=1, length=0.05, width=0.05, radius=0.5, height=2.3
            )
        )
        road1.add_object(
            xodr.Object(
                s=100, t=12, id=1, length=0.05, width=0.05, radius=0.5, height=2.3
            )
        )

        # create some signs (signals)
        road1.add_signal(
            xodr.Signal(
                s=100,
                t=-12,
                zOffset=2.3,
                orientation=xodr.Orientation.positive,
                country="se",
                Type="c",
                subtype="31",
                value=10,
                name="right_100_sign",
                id=1,
                unit="km/h",
            )
        )
        road1.add_signal(
            xodr.Signal(
                s=100,
                t=0,
                zOffset=2.3,
                orientation=xodr.Orientation.positive,
                country="se",
                Type="c",
                subtype="31",
                value=10,
                name="right_100_sign",
                id=1,
                unit="km/h",
            )
        )
        road1.add_signal(
            xodr.Signal(
                s=100,
                t=0,
                zOffset=2.3,
                orientation=xodr.Orientation.negative,
                country="se",
                Type="c",
                subtype="31",
                value=9,
                name="right_100_sign",
                id=1,
                unit="km/h",
            )
        )
        road1.add_signal(
            xodr.Signal(
                s=100,
                t=12,
                zOffset=2.3,
                orientation=xodr.Orientation.negative,
                country="se",
                Type="c",
                subtype="31",
                value=9,
                name="right_100_sign",
                id=1,
                unit="km/h",
            )
        )

        # add everything to the OpenDRIVE object
        odr = xodr.OpenDrive("my adjusted road")
        odr.add_road(road1)

        # adjust roads and lanes
        odr.adjust_roads_and_lanes()

        # adjust roadmarks (comment out to see difference)
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
    # esmini(sce, os.path.join("esmini"))
