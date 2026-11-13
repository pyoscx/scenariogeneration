"""
scenariogeneration
https://github.com/pyoscx/scenariogeneration

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2022 The scenariogeneration Authors.

"""

import numpy as np
import pytest
from math import isclose

from scenariogeneration import prettyprint, xodr

from .xml_validator import ValidationResponse, version_validation


def test_cross_section_surface():
    coefficients = xodr.CrossSectionCoefficients(1, 2, 3, 4)
    profile = xodr.CrossSectionStripProfile(
        xodr.CrossSectionProfileType.linear
    )
    width = xodr.CrossSectionStripWidth().add_coefficients(coefficients)
    profile.add_coefficients(coefficients)
    strip = xodr.CrossSectionStrip(width, profile)
    strips = xodr.CrossSectionSurfaceStrips().add_strip(strip)
    strips.add_strip(
        xodr.CrossSectionStrip(id=2, mode=xodr.StripMode.relative)
    )
    surface = xodr.CrossSectionSurface(
        strips,
        xodr.CrossSectionTOffset().add_coefficients(coefficients),
    )

    assert profile.get_element().tag == "linear"
    assert surface.get_element().find("tOffset/coefficients").attrib == {
        "a": "1",
        "b": "2",
        "c": "3",
        "d": "4",
        "s": "0",
    }
    assert surface.get_element().find("surfaceStrips/strip/linear") is not None
    assert (
        xodr.LateralProfile()
        .set_cross_section_surface(surface)
        .cross_section_surface
        == surface
    )

    with pytest.raises(TypeError):
        xodr.CrossSectionStripProfile("invalid")

    assert (
        version_validation(
            "t_road_lateralProfile_crossSectionSurface",
            surface,
            wanted_schema="xodr",
        )
        == ValidationResponse.OK
    )


def test_cross_section_polynomial_components():
    strip = xodr.CrossSectionStrip(id=-1)
    for profile_type in reversed(list(xodr.CrossSectionProfileType)):
        profile = xodr.CrossSectionStripProfile(profile_type)
        profile.add_coefficients(
            xodr.CrossSectionCoefficients(2, 0, 0, 0, s=50)
        )
        profile.add_coefficients(xodr.CrossSectionCoefficients(1, 0, 0, 0))
        strip.add_profile(profile)
    surface = xodr.CrossSectionSurface(
        xodr.CrossSectionSurfaceStrips().add_strip(strip)
    )
    element = surface.get_element().find("surfaceStrips/strip")
    assert element.attrib == {"id": "-1"}
    assert [item.tag for item in element] == [
        "constant",
        "linear",
        "quadratic",
        "cubic",
    ]
    for profile in element:
        assert [item.attrib["s"] for item in profile] == ["0", "50"]
    assert (
        version_validation(
            "t_road_lateralProfile_crossSectionSurface",
            surface,
            wanted_schema="xodr",
        )
        == ValidationResponse.OK
    )
    with pytest.raises(ValueError, match="only once"):
        strip.add_profile(
            xodr.CrossSectionStripProfile(xodr.CrossSectionProfileType.linear)
        )


@pytest.mark.parametrize("method", ["add_shape", "add_superelevation"])
def test_cross_section_excludes_other_lateral_profiles(method):
    surface = xodr.CrossSectionSurface(
        xodr.CrossSectionSurfaceStrips().add_strip(xodr.CrossSectionStrip())
    )
    polynomial = xodr.elevation._Poly3Profile(0, 0, 0, 0, 0)
    lateral = xodr.LateralProfile().set_cross_section_surface(surface)
    with pytest.raises(ValueError, match="cannot be combined"):
        getattr(lateral, method)(polynomial)
    lateral = xodr.LateralProfile()
    getattr(lateral, method)(polynomial)
    with pytest.raises(ValueError, match="cannot be combined"):
        lateral.set_cross_section_surface(surface)


def test_elevation_calculator_preserves_cross_section_surface():
    road = xodr.create_road(xodr.Line(10), 1)
    neighbor = xodr.create_road(xodr.Line(10), 2)
    road.add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.start)
    neighbor.add_predecessor(xodr.ElementType.road, 1, xodr.ContactPoint.end)
    neighbor.add_superelevation(0, 0.1, 0, 0, 0)
    surface = xodr.CrossSectionSurface(
        xodr.CrossSectionSurfaceStrips().add_strip(xodr.CrossSectionStrip())
    )
    road.lateralprofile.set_cross_section_surface(surface)
    calculator = xodr.ElevationCalculator(road)
    calculator.add_successor(neighbor)
    calculator.create_profile("superelevation")
    assert road.lateralprofile.cross_section_surface == surface
    assert not road.lateralprofile.superelevations
    assert not calculator._super_elevation_needed
    assert (
        version_validation(
            "t_road_lateralProfile", road.lateralprofile, wanted_schema="xodr"
        )
        == ValidationResponse.OK
    )


@pytest.mark.parametrize(
    "container_type", [xodr.CrossSectionStripWidth, xodr.CrossSectionTOffset]
)
def test_cross_section_coefficient_positions(container_type):
    container = container_type()
    with pytest.raises(ValueError, match="s=0"):
        container.get_element()
    container.add_coefficients(xodr.CrossSectionCoefficients(1, 0, 0, 0, s=10))
    with pytest.raises(ValueError, match="s=0"):
        container.get_element()
    container.add_coefficients(xodr.CrossSectionCoefficients(2, 0, 0, 0))
    assert [item.attrib["s"] for item in container.get_element()] == [
        "0",
        "10",
    ]
    container.add_coefficients(xodr.CrossSectionCoefficients(3, 0, 0, 0))
    with pytest.raises(ValueError, match="unique"):
        container.get_element()


@pytest.mark.parametrize(
    "strips",
    [
        [],
        [xodr.CrossSectionStrip(id=2)],
        [xodr.CrossSectionStrip(), xodr.CrossSectionStrip()],
        [xodr.CrossSectionStrip(), xodr.CrossSectionStrip(id=2)],
        [xodr.CrossSectionStrip(width=xodr.CrossSectionStripWidth())],
    ],
)
def test_cross_section_invalid_strip_layout(strips):
    container = xodr.CrossSectionSurfaceStrips()
    for strip in strips:
        container.add_strip(strip)
    with pytest.raises(ValueError):
        container.get_element()


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
        version_validation(
            "t_road_elevationProfile", elevation, wanted_schema="xodr"
        )
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
        version_validation(
            "t_road_lateralProfile", latprofile, wanted_schema="xodr"
        )
        == ValidationResponse.OK
    )


def test_elevation_calculator_single_suc_pre():
    main_road = xodr.create_road(xodr.Line(10), 1)
    connected_road = xodr.create_road(xodr.Line(10), 2)
    connected_road.add_elevation(0, 10, 1, 0, 0)
    main_road.add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.start)
    connected_road.add_predecessor(
        xodr.ElementType.road, 1, xodr.ContactPoint.end
    )

    ec = xodr.ElevationCalculator(main_road)
    ec.add_successor(connected_road)
    ec._create_elevation()
    assert isclose(main_road.elevationprofile.elevations[0].a, 0)
    assert isclose(main_road.elevationprofile.elevations[0].b, 1)


def test_elevation_calculator_single_suc_suc():
    main_road = xodr.create_road(xodr.Line(10), 1)
    connected_road = xodr.create_road(xodr.Line(10), 2)
    connected_road.add_elevation(0, 10, 1, 0, 0)
    main_road.add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.end)
    connected_road.add_successor(
        xodr.ElementType.road, 1, xodr.ContactPoint.end
    )

    ec = xodr.ElevationCalculator(main_road)
    ec.add_successor(connected_road)
    ec._create_elevation()
    assert isclose(main_road.elevationprofile.elevations[0].a, 30)
    assert isclose(main_road.elevationprofile.elevations[0].b, -1)


def test_elevation_calculator_single_pre_suc():
    main_road = xodr.create_road(xodr.Line(10), 1)
    connected_road = xodr.create_road(xodr.Line(10), 2)
    connected_road.add_elevation(0, 10, 1, 0, 0)
    main_road.add_predecessor(xodr.ElementType.road, 2, xodr.ContactPoint.end)
    connected_road.add_successor(
        xodr.ElementType.road, 1, xodr.ContactPoint.start
    )

    ec = xodr.ElevationCalculator(main_road)
    ec.add_predecessor(connected_road)
    ec._create_elevation()
    assert isclose(main_road.elevationprofile.elevations[0].a, 20)
    assert isclose(main_road.elevationprofile.elevations[0].b, 1)


def test_elevation_calculator_single_pre_pre():
    main_road = xodr.create_road(xodr.Line(10), 1)
    connected_road = xodr.create_road(xodr.Line(10), 2)
    connected_road.add_elevation(0, 10, 1, 0, 0)
    main_road.add_predecessor(
        xodr.ElementType.road, 2, xodr.ContactPoint.start
    )
    connected_road.add_predecessor(
        xodr.ElementType.road, 1, xodr.ContactPoint.start
    )

    ec = xodr.ElevationCalculator(main_road)
    ec.add_predecessor(connected_road)
    ec._create_elevation()
    assert isclose(main_road.elevationprofile.elevations[0].a, 10)
    assert isclose(main_road.elevationprofile.elevations[0].b, -1)


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
    assert isclose(main_road.elevationprofile.eval_at_s(0), 15)
    assert isclose(main_road.elevationprofile.eval_at_s(10), 10)
    assert isclose(main_road.elevationprofile.eval_derivative_at_s(10), 0)
    assert isclose(main_road.elevationprofile.eval_derivative_at_s(0), 1)


def test_elevation_calculator_pre_suc():
    main_road = xodr.create_road(xodr.Line(10), 1)

    suc_road = xodr.create_road(xodr.Line(10), 2)
    suc_road.add_elevation(0, 10, 0, 0, 0)
    pred_road = xodr.create_road(xodr.Line(10), 3)
    pred_road.add_elevation(0, 5, 1, 0, 0)
    main_road.add_predecessor(
        xodr.ElementType.road, 2, xodr.ContactPoint.start
    )
    main_road.add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.end)

    pred_road.add_predecessor(
        xodr.ElementType.road, 1, xodr.ContactPoint.start
    )
    suc_road.add_successor(xodr.ElementType.road, 1, xodr.ContactPoint.end)

    ec = xodr.ElevationCalculator(main_road)
    ec.add_predecessor(pred_road)
    ec.add_successor(suc_road)
    ec._create_elevation()
    assert isclose(main_road.elevationprofile.eval_at_s(0), 5)
    assert isclose(main_road.elevationprofile.eval_at_s(10), 10)
    assert isclose(main_road.elevationprofile.eval_derivative_at_s(10), 0)
    assert isclose(main_road.elevationprofile.eval_derivative_at_s(0), -1)


def test_elevation_calculator_single_pre_suc_junction_road():
    main_road = xodr.create_road(xodr.Line(10), 1)
    connected_road = xodr.create_road(xodr.Line(10), 2, road_type=100)
    connected_road.add_elevation(0, 10, 1, 0, 0)
    main_road.add_predecessor(xodr.ElementType.junction, 100)
    connected_road.add_successor(
        xodr.ElementType.road, 1, xodr.ContactPoint.start
    )

    ec = xodr.ElevationCalculator(main_road)
    ec.add_predecessor(connected_road)
    ec._create_elevation()
    assert isclose(main_road.elevationprofile.elevations[0].a, 20)
    assert isclose(main_road.elevationprofile.elevations[0].b, 1)


def test_elevation_calculator_single_pre_suc_junction_connection():
    main_road = xodr.create_road(xodr.Line(10), 1, road_type=100)
    connected_road = xodr.create_road(xodr.Line(10), 2)
    connected_road.add_elevation(0, 10, 1, 0, 0)
    main_road.add_predecessor(xodr.ElementType.road, 2, xodr.ContactPoint.end)
    connected_road.add_successor(xodr.ElementType.junction, 100)

    ec = xodr.ElevationCalculator(main_road)
    ec.add_predecessor(connected_road)
    ec._create_elevation()
    assert isclose(main_road.elevationprofile.elevations[0].a, 20)
    assert isclose(main_road.elevationprofile.elevations[0].b, 1)


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
    assert isclose(main_road.elevationprofile.elevations[0].a, 0)
    assert isclose(main_road.elevationprofile.elevations[0].b, 1)


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
    assert isclose(main_road.elevationprofile.elevations[0].a, 30)
    assert isclose(main_road.elevationprofile.elevations[0].b, -1)


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
    assert isclose(main_road.elevationprofile.elevations[0].a, 20)
    assert isclose(main_road.elevationprofile.elevations[0].b, 1)


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
    assert isclose(main_road.elevationprofile.elevations[0].a, 10)
    assert isclose(main_road.elevationprofile.elevations[0].b, -1)


def test_superelevation_calculator_single_suc_pre():
    main_road = xodr.create_road(xodr.Line(10), 1)
    connected_road = xodr.create_road(xodr.Line(10), 2)
    connected_road.add_superelevation(0, 1, 0, 0, 0)
    main_road.add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.start)
    connected_road.add_predecessor(
        xodr.ElementType.road, 1, xodr.ContactPoint.end
    )

    ec = xodr.ElevationCalculator(main_road)
    ec.add_successor(connected_road)
    ec._create_super_elevation()
    assert isclose(main_road.lateralprofile.superelevations[0].a, 1)


def test_superelevation_calculator_single_suc_suc():
    main_road = xodr.create_road(xodr.Line(10), 1)
    connected_road = xodr.create_road(xodr.Line(10), 2)
    connected_road.add_superelevation(0, 1, 0, 0, 0)
    main_road.add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.end)
    connected_road.add_successor(
        xodr.ElementType.road, 1, xodr.ContactPoint.end
    )

    ec = xodr.ElevationCalculator(main_road)
    ec.add_successor(connected_road)
    ec._create_super_elevation()
    assert isclose(main_road.lateralprofile.superelevations[0].a, -1)


def test_superelevation_calculator_single_pre_suc():
    main_road = xodr.create_road(xodr.Line(10), 1)
    connected_road = xodr.create_road(xodr.Line(10), 2)
    connected_road.add_superelevation(0, 1, 0, 0, 0)
    main_road.add_predecessor(xodr.ElementType.road, 2, xodr.ContactPoint.end)
    connected_road.add_successor(
        xodr.ElementType.road, 1, xodr.ContactPoint.start
    )

    ec = xodr.ElevationCalculator(main_road)
    ec.add_predecessor(connected_road)
    ec._create_super_elevation()
    assert isclose(main_road.lateralprofile.superelevations[0].a, 1)


def test_superelevation_calculator_single_pre_pre():
    main_road = xodr.create_road(xodr.Line(10), 1)
    connected_road = xodr.create_road(xodr.Line(10), 2)
    connected_road.add_superelevation(0, 1, 0, 0, 0)
    main_road.add_predecessor(
        xodr.ElementType.road, 2, xodr.ContactPoint.start
    )
    connected_road.add_predecessor(
        xodr.ElementType.road, 1, xodr.ContactPoint.start
    )

    ec = xodr.ElevationCalculator(main_road)
    ec.add_predecessor(connected_road)
    ec._create_super_elevation()
    assert isclose(main_road.lateralprofile.superelevations[0].a, -1)
