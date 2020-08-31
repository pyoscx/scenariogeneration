import pytest


import pyodrx 



def test_worldposition_noinput():
    spiral = pyodrx.Sprial(0,1)
    
    p = spiral.get_element()
    pyodrx.prettyprint(p)