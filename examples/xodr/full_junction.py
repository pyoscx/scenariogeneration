"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2022 The scenariogeneration Authors.

    An example, using the generators, showing how to create different symetric junctions,
    the numintersections can be changed to create different junctions

    In this example we can create a junction given

    Some features used:

    - create_road

    - CommonJunctionCreator

"""

import numpy as np
import os
from scenariogeneration import xodr, prettyprint, ScenarioGenerator


class Scenario(ScenarioGenerator):
    def __init__(self):
        super().__init__()

    def road(self, **kwargs):
        roads = []
        numintersections = 3
        nlanes = 1

        # setup junction creator
        junction_creator = xodr.CommonJunctionCreator(100, "my junction")

        # create some roads
        for i in range(numintersections):
            roads.append(
                xodr.create_road(
                    [xodr.Line(100)],
                    i,
                    center_road_mark=xodr.STD_ROADMARK_BROKEN,
                    left_lanes=nlanes,
                    right_lanes=nlanes,
                )
            )

            # add road to junciton
            junction_creator.add_incoming_road_circular_geometry(
                roads[i], 20, i * 2 * np.pi / numintersections, "successor"
            )

            # add connection to all previous roads
            for j in range(i):
                junction_creator.add_connection(j, i)

        odr = xodr.OpenDrive("myroad")

        for r in roads:
            odr.add_road(r)
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
