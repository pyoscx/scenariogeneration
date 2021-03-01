import pytest


from scenariogeneration import xosc as OSC
from scenariogeneration import prettyprint

@pytest.mark.parametrize("teststring",[OSC.DynamicsDimension.distance,OSC.DynamicsDimension.rate,OSC.DynamicsDimension.time])
def test_transition_dynamics(teststring):
    td = OSC.TransitionDynamics(OSC.DynamicsShapes.step,teststring,1)
    assert len(td.get_attributes()) == 3
    
    prettyprint(td.get_element())

# def test_transition_dynamics_faults():
#     with pytest.raises(ValueError):
#         OSC.TransitionDynamics('step','hej',1)

@pytest.mark.parametrize("testinp,results",[([None,None,None],0),([1,None,None],1),([1,None,2],2),([1,2,4],3) ] )
def test_dynamics_constraints(testinp,results):
    dyncon = OSC.DynamicsConstrains(max_deceleration=testinp[0],max_acceleration=testinp[1],max_speed=testinp[2])
    assert len(dyncon.get_attributes()) == results

@pytest.mark.parametrize("testinp,results",[([None,None,None],False),([1,None,None],True),([1,None,2],True),([1,2,4],True) ] )
def test_dynamics_constraints_filled(testinp,results):
    dyncon = OSC.DynamicsConstrains(max_deceleration=testinp[0],max_acceleration=testinp[1],max_speed=testinp[2])

    assert dyncon.is_filled() == results


@pytest.mark.parametrize("testinp,results",[([None,None,None,None],0),([1,None,None,None],1),([1,None,None,OSC.ReferenceContext.relative],2),([1,2,4,None],3),([1,2,4,OSC.ReferenceContext.absolute],4) ] )
def test_orientation(testinp,results):
    dyncon = OSC.Orientation(h=testinp[0],p=testinp[1],r=testinp[2],reference=testinp[3])
    print(dyncon.get_attributes())
    assert len(dyncon.get_attributes()) == results

@pytest.mark.parametrize("testinp,results",[([None,None,None,None],False),([1,None,None,None],True),([1,None,None,OSC.ReferenceContext.relative],True),([1,2,4,None],True),([1,2,4,OSC.ReferenceContext.absolute],True) ] )
def test_orientation_filled(testinp,results):
    dyncon = OSC.Orientation(h=testinp[0],p=testinp[1],r=testinp[2],reference=testinp[3])
    
    assert dyncon.is_filled() == results
    
# def test_orientation_failed():
#     with pytest.raises(ValueError):
#         OSC.Orientation(reference='hej')
   
def test_parameter():
    param = OSC.Parameter('stuffs',OSC.ParameterType.integer,'1')
    prettyprint(param.get_element())

def test_catalogreference():
    catref = OSC.CatalogReference('VehicleCatalog','S60')
    prettyprint(catref.get_element())
    catref.add_parameter_assignment('stuffs',1)
    prettyprint(catref.get_element())
    

def test_waypoint():
    wp = OSC.Waypoint(OSC.WorldPosition(),OSC.RouteStrategy.shortest)
    prettyprint(wp.get_element())

def test_route():
    route = OSC.Route('myroute')

    route.add_waypoint(OSC.WorldPosition(0,0,0,0,0,0),OSC.RouteStrategy.shortest)
    route.add_waypoint(OSC.WorldPosition(1,1,0,0,0,0),OSC.RouteStrategy.shortest)

    prettyprint(route.get_element())


def test_paramdeclaration():
    
    pardec = OSC.ParameterDeclarations()
    pardec.add_parameter(OSC.Parameter('myparam1',OSC.ParameterType.integer,'1'))
    pardec.add_parameter(OSC.Parameter('myparam1',OSC.ParameterType.double,'0.01'))
    prettyprint(pardec.get_element())

def test_parameterassignment():
    parass = OSC.ParameterAssignment('param1',1)
    prettyprint(parass.get_element())

def test_controller():
    prop = OSC.Properties()
    prop.add_property('mything','2')
    prop.add_property('theotherthing','true')

    cnt = OSC.Controller('mycontroler',prop)
    prettyprint(cnt.get_element())

def test_fileheader():
    fh = OSC.FileHeader('my_scenario','Mandolin')
    prettyprint(fh.get_element())

def test_polyline():
    positionlist = []
    positionlist.append(OSC.RelativeLanePosition(10,0.5,-3,'Ego'))
    positionlist.append(OSC.RelativeLanePosition(10,1,-3,'Ego'))
    positionlist.append(OSC.RelativeLanePosition(10,-1,-3,'Ego'))
    positionlist.append(OSC.RelativeLanePosition(10,0,-3,'Ego'))
    prettyprint(positionlist[0].get_element())
    polyline = OSC.Polyline([0,0.5,1,1.5],positionlist)
    prettyprint(polyline.get_element())


def test_clothoid():
    clot = OSC.Clothoid(1,0.1,10,OSC.WorldPosition(),0,1)
    prettyprint(clot.get_element())
    clot = OSC.Clothoid(1,0.1,10,OSC.WorldPosition())
    prettyprint(clot.get_element())
    
def test_trajectory():
    positionlist = []
    positionlist.append(OSC.RelativeLanePosition(10,0.5,-3,'Ego'))
    positionlist.append(OSC.RelativeLanePosition(10,1,-3,'Ego'))
    prettyprint(positionlist[0].get_element())
    polyline = OSC.Polyline([0,0.5],positionlist)
    traj = OSC.Trajectory('my_trajectory',False)
    traj.add_shape(polyline)
    prettyprint(traj.get_element())

def test_timeref():
    timeref = OSC.TimeReference(OSC.ReferenceContext.absolute,1,2)
    prettyprint(timeref.get_element())

def test_phase():
    p1 = OSC.Phase('myphase',1)
    prettyprint(p1.get_element())
    p1.add_signal_state('myid','red')
    p1.add_signal_state('myid','green')
    prettyprint(p1.get_element())

def test_TrafficSignalController():
    p1 = OSC.Phase('myphase',1)
    p1.add_signal_state('myid','red')
    p1.add_signal_state('myid','green')

    p2 = OSC.Phase('myphase2',3)
    p2.add_signal_state('myid2','yellow')
    p2.add_signal_state('myid2','green')
    p2.add_signal_state('myid2','red')
    prettyprint(p2.get_element())

    tsc = OSC.TrafficSignalController('my trafficlights')
    tsc.add_phase(p1)
    tsc.add_phase(p2)
    prettyprint(tsc.get_element())


def test_trafficdefinition():
    prop = OSC.Properties()
    prop.add_file('mycontrollerfile.xml')
    controller = OSC.Controller('mycontroller',prop)

    traffic = OSC.TrafficDefinition('my traffic')
    traffic.add_controller(controller,0.5)
    traffic.add_controller(OSC.CatalogReference('ControllerCatalog','my controller'),0.5)


    traffic.add_vehicle(OSC.VehicleCategory.car,0.9)
    traffic.add_vehicle(OSC.VehicleCategory.bicycle,0.1)

    prettyprint(traffic.get_element())

def test_weather():
    weather = OSC.Weather(OSC.CloudState.free,100,0,1,OSC.PrecipitationType.dry,1)
    prettyprint(weather.get_element())

def test_tod():
    tod = OSC.TimeOfDay(True,2020,10,1,18,30,30)
    prettyprint(tod.get_element())

def test_roadcondition():
    rc = OSC.RoadCondition(1)
    prettyprint(rc.get_element())

def test_environment():
    tod = OSC.TimeOfDay(True,2020,10,1,18,30,30)
    weather = OSC.Weather(OSC.CloudState.free,100,0,1,OSC.PrecipitationType.dry,1)
    rc = OSC.RoadCondition(1)

    env = OSC.Environment(tod,weather,rc)
    prettyprint(env.get_element())

def test_nurbs():
    cp1 = OSC.ControlPoint(OSC.WorldPosition(),1,0.1)
    cp2 = OSC.ControlPoint(OSC.WorldPosition(),2,0.2)
    cp3 = OSC.ControlPoint(OSC.WorldPosition(),3,0.3)


    nurb = OSC.Nurbs(2)
    nurb.add_control_point(cp1)
    nurb.add_control_point(cp2)
    nurb.add_control_point(cp3)
    nurb.add_knots([5,4,3,2,1])

    prettyprint(nurb.get_element())
