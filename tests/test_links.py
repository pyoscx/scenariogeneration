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


def test_connection():
    con = pyodrx.Connection(1,2,pyodrx.ContactPoint.start,5)

    con.add_lanelink(1,-1)
    con.add_lanelink(2,-2)

    pyodrx.prettyprint(con.get_element())

def test_junction():
    con1 = pyodrx.Connection(1,2,pyodrx.ContactPoint.start)

    con1.add_lanelink(1,-1)
    con1.add_lanelink(2,-2)

    con2 = pyodrx.Connection(2,1,pyodrx.ContactPoint.start)

    con2.add_lanelink(1,-1)
    con2.add_lanelink(2,-2)
    con2.add_lanelink(3,-3)

    junciton = pyodrx.Junction('',1)

    junciton.add_connection(con1)
    junciton.add_connection(con2)

    pyodrx.prettyprint(junciton.get_element())