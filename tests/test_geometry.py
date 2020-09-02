import pytest

import numpy as np

import pyodrx 

def test_line():
    line = pyodrx.Line(1)
    
    p = line.get_element()
    pyodrx.prettyprint(p)


@pytest.mark.parametrize("data, expdata",[\
([1, 0,0,0], [1,0,0]),\
([1, 0,0,np.pi/2], [0,1,np.pi/2]),\
([1, 1,1,0], [2,1,0]),\
([1, 1,1,0], [2,1,0]),\
([1, 1,1,np.pi/4], [1.7071067811865476,1.7071067811865476,np.pi/4]),\
])

# data: length, x, y, h
# expdata: new x, new y, new h
def test_line_calc(data,expdata):
    line = pyodrx.Line(data[0])
    x,y,h,l = line.get_end_data(data[1],data[2],data[3])
    assert pytest.approx(x,0.000001) == expdata[0]
    assert pytest.approx(y,0.000001) == expdata[1]
    assert pytest.approx(h,0.000001) == expdata[2]
    assert pytest.approx(l,0.000001) == data[0]

def test_spiral():
    spiral = pyodrx.Sprial(0,1)
    
    p = spiral.get_element()
    pyodrx.prettyprint(p)

def test_arc():
    arc = pyodrx.Arc(1,length = 1)
    
    p = arc.get_element()
    pyodrx.prettyprint(p)

    arc = pyodrx.Arc(1,angle = 1)
    
    p = arc.get_element()
    pyodrx.prettyprint(p)

@pytest.mark.parametrize("data, expdata",[\
([np.pi, 0,0,0,1], [0,2,np.pi]),
([2*np.pi, 0,0,0,1/2], [0,4,np.pi]),
([np.pi, 0,0,0,-1], [0,-2,-np.pi]),\
([np.pi/2, 0,0,0,1], [1,1,np.pi/2]),\
([np.pi/2, 1,1,0,1], [2,2,np.pi/2]),\
([np.pi/2, 0,0,-np.pi/2,1], [1,-1,0]),\
([np.pi/2, 0,0,-np.pi/2,-1], [-1,-1,-np.pi]),\
])

# data: length, x, y, h, curvature
# expdata: new x, new y, new h
def test_arc_calc_length(data,expdata):
    arc = pyodrx.Arc(data[4],data[0])
    x,y,h,l = arc.get_end_data(data[1],data[2],data[3])
    assert pytest.approx(x,0.000001) == expdata[0]
    assert pytest.approx(y,0.000001) == expdata[1]
    assert pytest.approx(h,0.000001) == expdata[2]
    assert pytest.approx(l,0.000001) == data[0]


@pytest.mark.parametrize("data, expdata",[\
([np.pi, 0,0,0,1], [0,2,np.pi,np.pi]),  
([np.pi, 0,0,0,1/2], [0,4,np.pi,np.pi*2]),
([np.pi/2, 1,1,0,1], [2,2,np.pi/2,np.pi/2]),
])
# data: angle, x, y, h, curvature
# expdata: new x, new y, new h, length
def test_arc_calc_angle(data,expdata):
    arc = pyodrx.Arc(data[4],angle=data[0])
    x,y,h,l = arc.get_end_data(data[1],data[2],data[3])
    assert pytest.approx(x,0.000001) == expdata[0]
    assert pytest.approx(y,0.000001) == expdata[1]
    assert pytest.approx(h,0.000001) == expdata[2]
    assert pytest.approx(l,0.000001) == expdata[3]
    # assert False
def test_polyparam():
    poly = pyodrx.ParamPoly3(1,2,3,4,5,6,7,8)
    
    p = poly.get_element()
    pyodrx.prettyprint(p)

@pytest.mark.parametrize("data, expdata",[\
([1, 0,0,0], [1,1,np.pi/4]),
])
# data: length, x, y, h
# expdata: new x, new y, new h
def test_arc_calc(data,expdata):
    arc = pyodrx.ParamPoly3(0,1,0,0,0,1,0,0)
    x,y,h = arc.get_end_data(data[0],data[1],data[2],data[3])
    assert pytest.approx(x,0.000001) == expdata[0]
    assert pytest.approx(y,0.000001) == expdata[1]
    assert pytest.approx(h,0.000001) == expdata[2]



def test_geometry():
    geom = pyodrx.geometry._Geometry(1,2,3,4,pyodrx.Line(1))
    p = geom.get_element()
    pyodrx.prettyprint(p)