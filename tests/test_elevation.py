import pytest
from scenariogeneration import xodr
from scenariogeneration import prettyprint


def test_poly3profile():
    profile = xodr.elevation._Poly3Profile(0,0,0,0,0)

    prettyprint(profile.get_element('elevation'))

    prettyprint(profile.get_element('superelevation'))

    profile = xodr.elevation._Poly3Profile(0,0,0,0,0,0)
    with pytest.raises(ValueError):
        prettyprint(profile.get_element('superelevation'))


def test_poly3profileshape():
    profile = xodr.elevation._Poly3Profile(0,0,0,0,0,0)

    prettyprint(profile.get_element('shape'))

    profile = xodr.elevation._Poly3Profile(0,0,0,0,0)
    with pytest.raises(ValueError):
        prettyprint(profile.get_element('shape'))

def test_elevationprofile():
    elevation = xodr.ElevationProfile()
    prettyprint(elevation.get_element())
    elevation.add_elevation(xodr.elevation._Poly3Profile(0,0,0,0,0))
    prettyprint(elevation.get_element())

def test_lateralprofile():
    latprofile = xodr.LateralProfile()
    prettyprint(latprofile.get_element())
    latprofile.add_shape(xodr.elevation._Poly3Profile(0,0,0,0,0,0))
    prettyprint(latprofile.get_element())
    latprofile.add_superelevation(xodr.elevation._Poly3Profile(0,0,0,0,0))
    prettyprint(latprofile.get_element())

