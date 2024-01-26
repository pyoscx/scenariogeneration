"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2022 The scenariogeneration Authors.

"""

import pytest
from scenariogeneration import xodr
from scenariogeneration import prettyprint
from .xml_validator import version_validation, ValidationResponse
import numpy as np


def test_poly3profile():
    profile = xodr.elevation._Poly3Profile(0, 0, 0, 0, 0)

    prettyprint(profile.get_element("elevation"))

    prettyprint(profile.get_element("superelevation"))

    profile1 = xodr.elevation._Poly3Profile(0, 0, 0, 0, 0, 0)
    with pytest.raises(ValueError):
        prettyprint(profile1.get_element("superelevation"))
    profile2 = xodr.elevation._Poly3Profile(0, 0, 0, 0, 0)
    profile3 = xodr.elevation._Poly3Profile(0, 0, 0, 0, 1)
    assert profile == profile2
    assert profile != profile3
    assert profile != profile1


def test_poly3profile_eval():
    profile = xodr.elevation._Poly3Profile(0, 1, 1, 0, 0)
    assert profile.eval_at_s(3) == 4
    assert profile.eval_derivative_at_s(3) == 1

    profile = xodr.elevation._Poly3Profile(5, 1, 1, 0, 0)
    assert profile.eval_at_s(8) == 4
    assert profile.eval_derivative_at_s(8) == 1


def test_poly3profile_eval():
    profile = xodr.elevation._Poly3Profile(0, 1, 1, 0, 0)
    assert profile.eval_at_s(3) == 4
    assert profile.eval_derivative_at_s(3) == 1

    profile = xodr.elevation._Poly3Profile(5, 1, 1, 0, 0)
    assert profile.eval_at_s(8) == 4
    assert profile.eval_derivative_at_s(8) == 1

    profile.elevation_type = "elevation"
    assert profile.eval_t_at_s(8, 1) == 4

    profile = xodr.elevation._Poly3Profile(
        0, np.pi / 4, 0, 0, 0, elevation_type="superelevation"
    )

    assert profile.eval_t_at_s(3, 1) == pytest.approx(1 / np.sqrt(2))
    assert profile.eval_t_at_s(3, -1) == pytest.approx(-1 / np.sqrt(2))


def test_poly3profileshape():
    profile = xodr.elevation._Poly3Profile(0, 0, 0, 0, 0, 0)

    prettyprint(profile.get_element("shape"))

    profile = xodr.elevation._Poly3Profile(0, 0, 0, 0, 0)
    with pytest.raises(ValueError):
        prettyprint(profile.get_element("shape"))


def test_elevationprofile():
    elevation = xodr.ElevationProfile()
    prettyprint(elevation.get_element())
    elevation.add_elevation(xodr.elevation._Poly3Profile(0, 0, 0, 0, 0))
    prettyprint(elevation.get_element())

    elevation2 = xodr.ElevationProfile()
    elevation2.add_elevation(xodr.elevation._Poly3Profile(0, 0, 0, 0, 0))

    elevation3 = xodr.ElevationProfile()
    elevation3.add_elevation(xodr.elevation._Poly3Profile(0, 0, 0, 0, 0))
    elevation3.add_userdata(xodr.UserData("stuffs", "morestuffs"))
    prettyprint(elevation3)
    assert elevation == elevation2
    assert elevation != elevation3

    assert (
        version_validation("t_road_elevationProfile", elevation, wanted_schema="xodr")
        == ValidationResponse.OK
    )


def test_elevationprofile_evaluation():
    elevation = xodr.ElevationProfile()
    elevation.add_elevation(xodr.elevation._Poly3Profile(0, 0, 0, 0, 0))
    elevation.add_elevation(xodr.elevation._Poly3Profile(10, 0, 1, 0, 0))
    elevation.add_elevation(xodr.elevation._Poly3Profile(20, 10, 2, 0, 0))
    assert elevation.eval_at_s(3) == 0
    assert elevation.eval_derivative_at_s(3) == 0
    assert elevation.eval_at_s(10) == 0
    assert elevation.eval_derivative_at_s(10) == 1
    assert elevation.eval_at_s(11) == 1
    assert elevation.eval_derivative_at_s(11) == 1
    assert elevation.eval_at_s(21) == 12
    assert elevation.eval_derivative_at_s(21) == 2


def test_elevationprofile_evaluation():
    elevation = xodr.ElevationProfile()
    elevation.add_elevation(xodr.elevation._Poly3Profile(0, 0, 0, 0, 0))
    elevation.add_elevation(xodr.elevation._Poly3Profile(10, 0, 1, 0, 0))
    elevation.add_elevation(xodr.elevation._Poly3Profile(20, 10, 2, 0, 0))
    assert elevation.eval_at_s(3) == 0
    assert elevation.eval_derivative_at_s(3) == 0
    assert elevation.eval_at_s(10) == 0
    assert elevation.eval_derivative_at_s(10) == 1
    assert elevation.eval_at_s(11) == 1
    assert elevation.eval_derivative_at_s(11) == 1
    assert elevation.eval_at_s(21) == 12
    assert elevation.eval_derivative_at_s(21) == 2


def test_lateralprofile():
    latprofile = xodr.LateralProfile()
    prettyprint(latprofile.get_element())
    latprofile.add_shape(xodr.elevation._Poly3Profile(0, 0, 0, 0, 0, 0))
    prettyprint(latprofile.get_element())
    latprofile.add_superelevation(xodr.elevation._Poly3Profile(0, 0, 0, 0, 0))
    prettyprint(latprofile.get_element())

    latprofile2 = xodr.LateralProfile()
    latprofile2.add_shape(xodr.elevation._Poly3Profile(0, 0, 0, 0, 0, 0))
    latprofile2.add_superelevation(xodr.elevation._Poly3Profile(0, 0, 0, 0, 0))

    latprofile3 = xodr.LateralProfile()
    latprofile3.add_userdata(xodr.UserData("stuffs", "morestuffs"))
    latprofile3.add_shape(xodr.elevation._Poly3Profile(0, 0, 0, 0, 0, 0))
    latprofile3.add_superelevation(xodr.elevation._Poly3Profile(0, 0, 0, 0, 3))
    prettyprint(latprofile3)

    assert latprofile2 == latprofile
    assert latprofile != latprofile3
    assert (
        version_validation("t_road_lateralProfile", latprofile, wanted_schema="xodr")
        == ValidationResponse.OK
    )


def test_elevation_calculator_single_suc_pre():
    main_road = xodr.create_road(xodr.Line(10), 1)
    connected_road = xodr.create_road(xodr.Line(10), 2)
    connected_road.add_elevation(0, 10, 1, 0, 0)
    main_road.add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.start)
    connected_road.add_predecessor(xodr.ElementType.road, 1, xodr.ContactPoint.end)

    ec = xodr.ElevationCalculator(main_road)
    ec.add_successor(connected_road)
    ec._create_elevation()
    assert main_road.elevationprofile.elevations[0].a == 0
    assert main_road.elevationprofile.elevations[0].b == 1


def test_elevation_calculator_single_suc_suc():
    main_road = xodr.create_road(xodr.Line(10), 1)
    connected_road = xodr.create_road(xodr.Line(10), 2)
    connected_road.add_elevation(0, 10, 1, 0, 0)
    main_road.add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.end)
    connected_road.add_successor(xodr.ElementType.road, 1, xodr.ContactPoint.end)

    ec = xodr.ElevationCalculator(main_road)
    ec.add_successor(connected_road)
    ec._create_elevation()
    assert main_road.elevationprofile.elevations[0].a == 30
    assert main_road.elevationprofile.elevations[0].b == -1


def test_elevation_calculator_single_pre_suc():
    main_road = xodr.create_road(xodr.Line(10), 1)
    connected_road = xodr.create_road(xodr.Line(10), 2)
    connected_road.add_elevation(0, 10, 1, 0, 0)
    main_road.add_predecessor(xodr.ElementType.road, 2, xodr.ContactPoint.end)
    connected_road.add_successor(xodr.ElementType.road, 1, xodr.ContactPoint.start)

    ec = xodr.ElevationCalculator(main_road)
    ec.add_predecessor(connected_road)
    ec._create_elevation()
    assert main_road.elevationprofile.elevations[0].a == 20
    assert main_road.elevationprofile.elevations[0].b == 1


def test_elevation_calculator_single_pre_pre():
    main_road = xodr.create_road(xodr.Line(10), 1)
    connected_road = xodr.create_road(xodr.Line(10), 2)
    connected_road.add_elevation(0, 10, 1, 0, 0)
    main_road.add_predecessor(xodr.ElementType.road, 2, xodr.ContactPoint.start)
    connected_road.add_predecessor(xodr.ElementType.road, 1, xodr.ContactPoint.start)

    ec = xodr.ElevationCalculator(main_road)
    ec.add_predecessor(connected_road)
    ec._create_elevation()
    assert main_road.elevationprofile.elevations[0].a == 10
    assert main_road.elevationprofile.elevations[0].b == -1


def test_elevation_calculator_suc_pre():
    main_road = xodr.create_road(xodr.Line(10), 1)

    suc_road = xodr.create_road(xodr.Line(10), 2)
    suc_road.add_elevation(0, 10, 0, 0, 0)
    pred_road = xodr.create_road(xodr.Line(10), 3)
    pred_road.add_elevation(0, 5, 1, 0, 0)
    main_road.add_predecessor(xodr.ElementType.road, 2, xodr.ContactPoint.end)
    main_road.add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.start)

    pred_road.add_successor(xodr.ElementType.road, 1, xodr.ContactPoint.start)
    suc_road.add_predecessor(xodr.ElementType.road, 1, xodr.ContactPoint.end)

    ec = xodr.ElevationCalculator(main_road)
    ec.add_predecessor(pred_road)
    ec.add_successor(suc_road)
    ec._create_elevation()
    assert main_road.elevationprofile.eval_at_s(0) == 15
    assert main_road.elevationprofile.eval_at_s(10) == 10
    assert main_road.elevationprofile.eval_derivative_at_s(10) == 0
    assert main_road.elevationprofile.eval_derivative_at_s(0) == 1


def test_elevation_calculator_pre_suc():
    main_road = xodr.create_road(xodr.Line(10), 1)

    suc_road = xodr.create_road(xodr.Line(10), 2)
    suc_road.add_elevation(0, 10, 0, 0, 0)
    pred_road = xodr.create_road(xodr.Line(10), 3)
    pred_road.add_elevation(0, 5, 1, 0, 0)
    main_road.add_predecessor(xodr.ElementType.road, 2, xodr.ContactPoint.start)
    main_road.add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.end)

    pred_road.add_predecessor(xodr.ElementType.road, 1, xodr.ContactPoint.start)
    suc_road.add_successor(xodr.ElementType.road, 1, xodr.ContactPoint.end)

    ec = xodr.ElevationCalculator(main_road)
    ec.add_predecessor(pred_road)
    ec.add_successor(suc_road)
    ec._create_elevation()
    assert main_road.elevationprofile.eval_at_s(0) == 5
    assert main_road.elevationprofile.eval_at_s(10) == 10
    assert main_road.elevationprofile.eval_derivative_at_s(10) == 0
    assert main_road.elevationprofile.eval_derivative_at_s(0) == -1


def test_elevation_calculator_single_pre_suc_junction_road():
    main_road = xodr.create_road(xodr.Line(10), 1)
    connected_road = xodr.create_road(xodr.Line(10), 2, road_type=100)
    connected_road.add_elevation(0, 10, 1, 0, 0)
    main_road.add_predecessor(xodr.ElementType.junction, 100)
    connected_road.add_successor(xodr.ElementType.road, 1, xodr.ContactPoint.start)

    ec = xodr.ElevationCalculator(main_road)
    ec.add_predecessor(connected_road)
    ec._create_elevation()
    assert main_road.elevationprofile.elevations[0].a == 20
    assert main_road.elevationprofile.elevations[0].b == 1


def test_elevation_calculator_single_pre_suc_junction_connection():
    main_road = xodr.create_road(xodr.Line(10), 1, road_type=100)
    connected_road = xodr.create_road(xodr.Line(10), 2)
    connected_road.add_elevation(0, 10, 1, 0, 0)
    main_road.add_predecessor(xodr.ElementType.road, 2, xodr.ContactPoint.end)
    connected_road.add_successor(xodr.ElementType.junction, 100)

    ec = xodr.ElevationCalculator(main_road)
    ec.add_predecessor(connected_road)
    ec._create_elevation()
    assert main_road.elevationprofile.elevations[0].a == 20
    assert main_road.elevationprofile.elevations[0].b == 1


def test_elevation_calculator_single_suc_pre_dir_junc():
    main_road = xodr.create_road(xodr.Line(10), 1)
    connected_road = xodr.create_road(xodr.Line(10), 2)
    connected_road.add_elevation(0, 10, 1, 0, 0)
    main_road.add_successor(xodr.ElementType.junction, 100)
    main_road.succ_direct_junction[2] = 0
    connected_road.add_predecessor(xodr.ElementType.junction, 100)
    connected_road.pred_direct_junction[1] = 0
    ec = xodr.ElevationCalculator(main_road)
    ec.add_successor(connected_road)
    ec._create_elevation()
    assert main_road.elevationprofile.elevations[0].a == 0
    assert main_road.elevationprofile.elevations[0].b == 1


def test_elevation_calculator_single_suc_suc_dir_junc():
    main_road = xodr.create_road(xodr.Line(10), 1)
    connected_road = xodr.create_road(xodr.Line(10), 2)
    connected_road.add_elevation(0, 10, 1, 0, 0)
    main_road.add_successor(xodr.ElementType.junction, 100)
    main_road.succ_direct_junction[2] = 0
    connected_road.add_successor(xodr.ElementType.junction, 100)
    connected_road.succ_direct_junction[1] = 0
    ec = xodr.ElevationCalculator(main_road)
    ec.add_successor(connected_road)
    ec._create_elevation()
    assert main_road.elevationprofile.elevations[0].a == 30
    assert main_road.elevationprofile.elevations[0].b == -1


def test_elevation_calculator_single_pre_suc_dir_junc():
    main_road = xodr.create_road(xodr.Line(10), 1)
    connected_road = xodr.create_road(xodr.Line(10), 2)
    connected_road.add_elevation(0, 10, 1, 0, 0)
    main_road.add_predecessor(xodr.ElementType.junction, 100)
    main_road.pred_direct_junction[2] = 0
    connected_road.add_successor(xodr.ElementType.junction, 100)
    connected_road.succ_direct_junction[1] = 0
    ec = xodr.ElevationCalculator(main_road)
    ec.add_predecessor(connected_road)
    ec._create_elevation()
    assert main_road.elevationprofile.elevations[0].a == 20
    assert main_road.elevationprofile.elevations[0].b == 1


def test_elevation_calculator_single_pre_pre_dir_junc():
    main_road = xodr.create_road(xodr.Line(10), 1)
    connected_road = xodr.create_road(xodr.Line(10), 2)
    connected_road.add_elevation(0, 10, 1, 0, 0)
    main_road.add_predecessor(xodr.ElementType.junction, 100)
    main_road.pred_direct_junction[2] = 0
    connected_road.add_predecessor(xodr.ElementType.junction, 100)
    connected_road.pred_direct_junction[1] = 0
    ec = xodr.ElevationCalculator(main_road)
    ec.add_predecessor(connected_road)
    ec._create_elevation()
    assert main_road.elevationprofile.elevations[0].a == 10
    assert main_road.elevationprofile.elevations[0].b == -1


def test_superelevation_calculator_single_suc_pre():
    main_road = xodr.create_road(xodr.Line(10), 1)
    connected_road = xodr.create_road(xodr.Line(10), 2)
    connected_road.add_superelevation(0, 1, 0, 0, 0)
    main_road.add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.start)
    connected_road.add_predecessor(xodr.ElementType.road, 1, xodr.ContactPoint.end)

    ec = xodr.ElevationCalculator(main_road)
    ec.add_successor(connected_road)
    ec._create_super_elevation()
    assert main_road.lateralprofile.superelevations[0].a == 1


def test_superelevation_calculator_single_suc_suc():
    main_road = xodr.create_road(xodr.Line(10), 1)
    connected_road = xodr.create_road(xodr.Line(10), 2)
    connected_road.add_superelevation(0, 1, 0, 0, 0)
    main_road.add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.end)
    connected_road.add_successor(xodr.ElementType.road, 1, xodr.ContactPoint.end)

    ec = xodr.ElevationCalculator(main_road)
    ec.add_successor(connected_road)
    ec._create_super_elevation()
    assert main_road.lateralprofile.superelevations[0].a == -1


def test_superelevation_calculator_single_pre_suc():
    main_road = xodr.create_road(xodr.Line(10), 1)
    connected_road = xodr.create_road(xodr.Line(10), 2)
    connected_road.add_superelevation(0, 1, 0, 0, 0)
    main_road.add_predecessor(xodr.ElementType.road, 2, xodr.ContactPoint.end)
    connected_road.add_successor(xodr.ElementType.road, 1, xodr.ContactPoint.start)

    ec = xodr.ElevationCalculator(main_road)
    ec.add_predecessor(connected_road)
    ec._create_super_elevation()
    assert main_road.lateralprofile.superelevations[0].a == 1


def test_superelevation_calculator_single_pre_pre():
    main_road = xodr.create_road(xodr.Line(10), 1)
    connected_road = xodr.create_road(xodr.Line(10), 2)
    connected_road.add_superelevation(0, 1, 0, 0, 0)
    main_road.add_predecessor(xodr.ElementType.road, 2, xodr.ContactPoint.start)
    connected_road.add_predecessor(xodr.ElementType.road, 1, xodr.ContactPoint.start)

    ec = xodr.ElevationCalculator(main_road)
    ec.add_predecessor(connected_road)
    ec._create_super_elevation()
    assert main_road.lateralprofile.superelevations[0].a == -1
