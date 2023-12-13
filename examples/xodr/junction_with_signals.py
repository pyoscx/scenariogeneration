"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2022 The scenariogeneration Authors.

    Example of how to create a junction but adding signals to the junction


"""

# Same approach to creating a junction as "full_junction.py" but with signals for each incoming road.
import numpy as np
import os
from scenariogeneration import xodr, prettyprint, ScenarioGenerator


class Scenario(ScenarioGenerator):
    def __init__(self):
        super().__init__()

    def road(self, **kwargs):
        roads = []
        incoming_roads = 4
        nlanes = 1
        # setup junction creator
        junction_creator = xodr.CommonJunctionCreator(100, "my junction")

        # create roads and connections
        for i in range(incoming_roads):
            roads.append(
                xodr.create_road(
                    [xodr.Line(100)],
                    i,
                    center_road_mark=xodr.STD_ROADMARK_BROKEN,
                    left_lanes=nlanes,
                    right_lanes=nlanes,
                )
            )
            roads[-1].add_signal(
                xodr.Signal(s=98.0, t=-4, country="USA", Type="R1", subtype="1")
            )

            # add road to junciton
            junction_creator.add_incoming_road_circular_geometry(
                roads[i], 20, i * 2 * np.pi / incoming_roads, "successor"
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

    # write the OpenSCENARIO file as xosc using current script name
    sce.generate(".")

    # uncomment the following lines to display the scenario using esmini
    # from scenariogeneration import esmini
    # esmini(sce,os.path.join('esmini'))
