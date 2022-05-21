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
    elevation3.add_elevation(xodr.elevation._Poly3Profile(0, 0, 0, 1, 0))
    assert elevation == elevation2
    assert elevation != elevation3


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
    latprofile3.add_shape(xodr.elevation._Poly3Profile(0, 0, 0, 0, 0, 0))
    latprofile3.add_superelevation(xodr.elevation._Poly3Profile(0, 0, 0, 0, 3))

    assert latprofile2 == latprofile
    assert latprofile != latprofile3
