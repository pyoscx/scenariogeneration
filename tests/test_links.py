import pytest
import pyodrx
def test_link():
    link = pyodrx.links._Link('successor','1')
    
    pyodrx.prettyprint(link.get_element())

    link = pyodrx.links._Link('successor','1',element_type=pyodrx.ElementType.road,contact_point=pyodrx.ContactPoint.start)
    
    pyodrx.prettyprint(link.get_element())

def test_links():

    links = pyodrx.links._Links()
    pyodrx.prettyprint(links.get_element())
    link = pyodrx.links._Link('successor','1')
    links.add_link(link)    
    pyodrx.prettyprint(links.get_element())


