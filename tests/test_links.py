import pytest
import pyodrx
def test_links():
    link = pyodrx.links._Link('successor','1')
    
    pyodrx.prettyprint(link.get_element())

    link = pyodrx.links._Link('successor','1',element_type=pyodrx.ElementType.road,contact_point=pyodrx.ContactPoint.start)
    
    pyodrx.prettyprint(link.get_element())
