"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.

"""
from .enumerations import ContactPoint


def get_lane_sec_and_s_for_lane_calc(road, contact_point):
    """Helping function to get a lane_section and s coordinate for calculations, at either the end or start of a road

    Parameters
    ----------
        road (Road): the road to be used

        contact_point (ContactPoint): start or end of the road

    Returns
    -------
        lanesection (int): 0 or -1

        s (float): the s coordinate at start or end of the road
    """

    relevant_s = 0
    if contact_point == ContactPoint.start:
        relevant_lanesection = 0  # since we are at the start the first lane section is relevant for determining widths for lane offset
    elif contact_point == ContactPoint.end:
        relevant_lanesection = (
            -1
        )  # since we are at the end the last lane section is relevant for determining widths for lane offset

        for geom in road.planview._raw_geometries:
            relevant_s += geom.length

    return relevant_lanesection, relevant_s
