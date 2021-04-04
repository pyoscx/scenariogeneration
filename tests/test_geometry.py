import pytest

import numpy as np

from scenariogeneration import xodr as pyodrx
from scenariogeneration import prettyprint
def test_line():
    line = pyodrx.Line(1)
    
    p = line.get_element()
    prettyprint(p)


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
    spiral = pyodrx.Spiral(0,1, 10)
    
    p = spiral.get_element()
    prettyprint(p)

def test_spiral_inputs():
    cloth = pyodrx.Spiral(0.0,0.05,10.0)
    assert cloth.curvstart == 0
    assert cloth.curvend == 0.05
    assert cloth.length == 10



@pytest.mark.parametrize("data, expdata",[\
([0, 0   , 10, 0, 0, 0], [10,0,0]),
([0, 0   , 10, 10, 0, 0], [20,0,0]),
([0, 0   , 10, 0, 10, 0], [10,10,0]),
([0, 0   , 10, 0, 0, np.pi/2], [0,10,np.pi/2]),
([0, 0   , 10, 0, 0, -np.pi/2], [0,-10,-np.pi/2]),
])

# data: curvestart, curveend, length, x, y, initial heading
# expdata: new x, new y, new h, new l
def test_spiral_zero_curv(data,expdata):
    cloth = pyodrx.Spiral(data[0], data[1], data[2])
    x,y,h,l = cloth.get_end_data(data[3], data[4], data[5])

    assert pytest.approx(x,0.000001) == expdata[0]
    assert pytest.approx(y,0.000001) == expdata[1]
    assert pytest.approx(h,0.000001) == expdata[2]
    assert pytest.approx(l,0.000001) == data[2]

@pytest.mark.parametrize("data, expdata",[\
([0, 0.05, 10, 0, 0, 0], [9.937680,0.829620,0.25]),\
([0, -0.05, 10, 0, 0, 0], [9.937680,-0.829620,-0.25]),\
([0, 0.08, 20, 0, 0, 0], [18.757370,5.094433,0.8]),\
([0, -0.08, 20, 0, 0, 0], [18.757370,-5.094433,-0.8]),\
([0, 0.05, 10, 10, 0, 0], [19.937680,0.829620,0.25]),\
([0, 0.05, 10, 0, 10, 0], [9.9376805,0.829620+10,0.25]),\
([0, 0.05, 10, -10, 0, 0], [-0.062319415,0.829620,0.25]),\
([0, 0.05, 10, 0, -10, 0], [9.937680,-9.17037951,0.25]),\
([0, 0.05, 10, 0, 0, np.pi/2], [-0.829620,9.937680,0.25+np.pi/2]),\
([0, 0.05, 10, 0, 0, -np.pi/2], [0.829620,-9.937680,-np.pi/2+0.25]),\
])

# data: curvestart, curveend, length, x, y, initial heading
# expdata: new x, new y, new h, new l
def test_spiral_from_zero_curv(data,expdata):
    cloth = pyodrx.Spiral(data[0], data[1], data[2])
    x,y,h,l = cloth.get_end_data(data[3], data[4], data[5])

    assert pytest.approx(x,0.000001) == expdata[0]
    assert pytest.approx(y,0.000001) == expdata[1]
    assert pytest.approx(h,0.000001) == expdata[2]
    assert pytest.approx(l,0.000001) == data[2]

@pytest.mark.parametrize("data, expdata",[\
([0.05, 0, 10, 0, 0, 0], [9.833993,1.654791,0.25]),\
([-0.05, 0, 10, 0, 0, 0], [9.833993,-1.654791,-0.25]),\
([0.05, 0, 20, 0, 0, 0], [18.687683,6.478104,0.5]),\
([-0.05, 0, 20, 0, 0, 0], [18.687683,-6.478104, -0.5]),\
])

# data: curvestart, curveend, length, x, y, initial heading
# expdata: new x, new y, new h, new l
def test_spiral_to_zero_curv(data,expdata):
    cloth = pyodrx.Spiral(data[0], data[1], data[2])
    x,y,h,l = cloth.get_end_data(data[3], data[4], data[5])

    assert pytest.approx(x,0.000001) == expdata[0]
    assert pytest.approx(y,0.000001) == expdata[1]
    assert pytest.approx(h,0.000001) == expdata[2]
    assert pytest.approx(l,0.000001) == data[2]

@pytest.mark.parametrize("data, expdata",[\
([-0.05, 0.05, 10, 0, 0, 0], [9.958374, -0.831846, 0.0]),\
([0.05, -0.05, 10, 0, 0, 0], [9.958374, 0.831846, 0.0]),\
])

# data: curvestart, curveend, length, x, y, initial heading
# expdata: new x, new y, new h, new l
def test_spiral_from_neg_to_pos_curv(data,expdata):
    cloth = pyodrx.Spiral(data[0], data[1], data[2])
    x,y,h,l = cloth.get_end_data(data[3], data[4], data[5])

    assert pytest.approx(x,0.000001) == expdata[0]
    assert pytest.approx(y,0.000001) == expdata[1]
    assert pytest.approx(h,0.000001) == expdata[2]
    assert pytest.approx(l,0.000001) == data[2]

def test_arc():
    arc = pyodrx.Arc(1,length = 1)
    
    p = arc.get_element()
    prettyprint(p)

    arc = pyodrx.Arc(1,angle = 1)
    
    p = arc.get_element()
    prettyprint(p)

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
([-np.pi, 0,0,0,-1], [0,-2,-np.pi,np.pi]),
([-np.pi, 0,0,0,-0.5], [0,-4,-np.pi,2*np.pi]),
([-np.pi/2, 0,0,0,-1], [1,-1,-np.pi/2,np.pi/2]),
([-np.pi, 1,0,0,-1], [1,-2,-np.pi,np.pi]),
([-np.pi, 0,1,0,-1], [0,-1,-np.pi,np.pi]),
([-np.pi, 0,0,np.pi,-1], [0,2,0,np.pi]),
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
    prettyprint(p)

@pytest.mark.parametrize("data, expdata",[\
([1, 0,0,0], [1,1,np.pi/4]),
])
# data: length, x, y, h
# expdata: new x, new y, new h
def test_arc_calc(data,expdata):
    arc = pyodrx.ParamPoly3(0,1,0,0,0,1,0,0,'arcLength',data[0])
    x,y,h,l = arc.get_end_data(data[1],data[2],data[3])
    assert pytest.approx(x,0.000001) == expdata[0]
    assert pytest.approx(y,0.000001) == expdata[1]
    assert pytest.approx(h,0.000001) == expdata[2]
    assert pytest.approx(l,0.000001) == data[0]


def test_geometry():
    geom = pyodrx.geometry._Geometry(1,2,3,4,pyodrx.Line(1))
    p = geom.get_element()
    prettyprint(p)

@pytest.mark.parametrize("data",[\
([100, 0,0,0]),
([100, 10, 0, 0]),
([100, -10, 0, 0]),
([100, 0, 10, 0]),
([100, 0, -10, 0]),
([100, 0, 0, np.pi]),
([100, 0, 0, -np.pi]),
])

def test_inverted_Line(data):
    line = pyodrx.Line(data[0])

    end_x,end_y,end_h,_ = line.get_end_data(data[1],data[2],data[3])

    end_h += np.pi 

    start_x,start_y,start_h,_ = line.get_start_data(end_x,end_y,end_h)

    start_h -= np.pi

    assert pytest.approx(start_x, 0.000001) == data[1]
    assert pytest.approx(start_y, 0.000001) == data[2]
    assert pytest.approx(start_h, 0.1) == data[3] 

@pytest.mark.parametrize("data",[\
([1, np.pi, 0,0,0]), 
([1, np.pi/2, 0,0,0]),
([1, np.pi, 1,0,0]),
([1, np.pi, -1,0,0]),
([1, np.pi, 0,1,0]),
([1, np.pi, 0,-1,0]),
([1, np.pi, 0,0,1]),
([1, np.pi, 0,0,-1]),
([-1, -np.pi, 0,0,0]),
([-1, -np.pi, 1,0,0]),
([-1, -np.pi, -1,0,0]),
([-1, -np.pi, 0,1,0]),
([-1, -np.pi, 0,-1,0]),
([-1, -np.pi, 0,0,1]),
([-1, -np.pi, 0,0,-1]),
])

def test_inverted_Arc(data):
    
    arc = pyodrx.Arc(data[0],angle=data[1])

    end_x,end_y,end_h,_ = arc.get_end_data(data[2],data[3],data[4])

    end_h += np.pi 

    start_x,start_y,start_h,_ = arc.get_start_data(end_x,end_y,end_h)

    start_h -= np.pi

    assert pytest.approx(start_x, 0.000001) == data[2]
    assert pytest.approx(start_y, 0.000001) == data[3]
    assert pytest.approx(start_h, 0.00001) == data[4] 


@pytest.mark.parametrize("data",[\
([0.01, 0.05,15, 0, 0, 0]),
([0.01, -0.05,15, 0, 0, 0]),
([-0.01, 0.05,15, 0, 0, 0]),
([-0.01, -0.05,15, 0, 0, 0]),
([0.01, 0.05,15, 1, 0, 0]),
([0.01, 0.05,15, 0, 1, 0]),
([0.01, 0.05,15, 0, 0, 1]),
([0.01, 0.05,15, -1, 0, 0]),
([0.01, 0.05,15, 0, -1, 0]),
([0.01, 0.05,15, 0, 0, -1]),
([-0.01, -0.05,15, 1, 0, 0]),
([-0.01, -0.05,15, 0, 1, 0]),
([-0.01, -0.05,15, 0, 0, 1]),
([-0.01, -0.05,15, -1, 0, 0]),
([-0.01, -0.05,15, 0, -1, 0]),
([-0.01, -0.05,15, 0, 0, -1]),

])

def test_inverted_Spiral(data):
    cloth = pyodrx.Spiral(data[0], data[1], data[2])

    end_x,end_y,end_h,_ = cloth.get_end_data(data[3],data[4],data[5])

    end_h += np.pi 

    start_x,start_y,start_h,_ = cloth.get_start_data(end_x,end_y,end_h)

    start_h -= np.pi

    assert pytest.approx(start_x, 0.000001) == data[3]
    assert pytest.approx(start_y, 0.000001) == data[4]
    assert pytest.approx(start_h, 0.000001) == data[5] 


@pytest.mark.parametrize("data, expdata",[\
([100,0,0,0], [100,0,0]),\
([100,10,10,0], [110,10,0]),\
([100,10,10,np.pi/2], [10,110,np.pi/2]),\
])

# data: length, xstart,ystart,headingstart
# expdata: end x, end y, end h
def test_manual_geometry(data,expdata):
    planview = pyodrx.PlanView()
    planview.add_fixed_geometry(pyodrx.Line(data[0]),data[1],data[2],data[3])

    x,y,h = planview.get_end_point()
    assert pytest.approx(x, 0.000001) == expdata[0]
    assert pytest.approx(y, 0.000001) == expdata[1]
    assert pytest.approx(h, 0.000001) == expdata[2]
    x,y,h = planview.get_start_point()
    assert pytest.approx(x, 0.000001) == data[1]
    assert pytest.approx(y, 0.000001) == data[2]
    assert pytest.approx(h, 0.000001) == data[3]
    
