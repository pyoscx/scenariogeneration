import pytest


import pyoscx as OSC




@pytest.mark.parametrize("teststring",['linear','cubic','sinusoidal','step'])
def testDynamicsShape(teststring):
    OSC.DynamicsShape(teststring,1)

def test_dynamicsShape_wronginput():
    with pytest.raises(ValueError):
        OSC.DynamicsShape('hej',1)

@pytest.mark.parametrize("teststring",['distance','rate','time'])
def test_transition_dynamics(teststring):
    td = OSC.TransitionDynamics('step',1,teststring,1)
    assert len(td.get_attributes()) == 3
    
    OSC.prettyprint(td.get_element())

def test_transition_dynamics_faults():
    with pytest.raises(ValueError):
        OSC.TransitionDynamics('step',1,'hej',1)

@pytest.mark.parametrize("testinp,results",[([None,None,None],0),([1,None,None],1),([1,None,2],2),([1,2,4],3) ] )
def test_dynamics_constraints(testinp,results):
    dyncon = OSC.DynamicsConstrains(max_deceleration=testinp[0],max_acceleration=testinp[1],max_speed=testinp[2])
    assert len(dyncon.get_attributes()) == results

@pytest.mark.parametrize("testinp,results",[([None,None,None],False),([1,None,None],True),([1,None,2],True),([1,2,4],True) ] )
def test_dynamics_constraints_filled(testinp,results):
    dyncon = OSC.DynamicsConstrains(max_deceleration=testinp[0],max_acceleration=testinp[1],max_speed=testinp[2])

    assert dyncon.is_filled() == results


@pytest.mark.parametrize("testinp,results",[([None,None,None,None],0),([1,None,None,None],1),([1,None,None,'relative'],2),([1,2,4,None],3),([1,2,4,'absolute'],4) ] )
def test_orientation(testinp,results):
    dyncon = OSC.Orientation(h=testinp[0],p=testinp[1],r=testinp[2],reference=testinp[3])
    print(dyncon.get_attributes())
    assert len(dyncon.get_attributes()) == results

@pytest.mark.parametrize("testinp,results",[([None,None,None,None],False),([1,None,None,None],True),([1,None,None,'relative'],True),([1,2,4,None],True),([1,2,4,'absolute'],True) ] )
def test_orientation_filled(testinp,results):
    dyncon = OSC.Orientation(h=testinp[0],p=testinp[1],r=testinp[2],reference=testinp[3])
    
    assert dyncon.is_filled() == results
    


def test_orientation_failed():
    with pytest.raises(ValueError):
        OSC.Orientation(reference='hej')
   
    