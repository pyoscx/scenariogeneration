import pytest


from scenariogeneration import xosc as OSC
from scenariogeneration import prettyprint

@pytest.mark.parametrize("teststring",[OSC.DynamicsDimension.distance,OSC.DynamicsDimension.rate,OSC.DynamicsDimension.time])
def test_transition_dynamics(teststring):
    td = OSC.TransitionDynamics(OSC.DynamicsShapes.step,teststring,1)
    assert len(td.get_attributes()) == 3

    prettyprint(td.get_element())

    td2 = OSC.TransitionDynamics(OSC.DynamicsShapes.step,teststring,1)
    td3 = OSC.TransitionDynamics(OSC.DynamicsShapes.step,teststring,2)
    
    assert td == td2
    assert td != td3

@pytest.mark.parametrize("testinp,results",[([None,None,None],0),([1,None,None],1),([1,None,2],2),([1,2,4],3) ] )
def test_dynamics_constraints(testinp,results):
    dyncon = OSC.DynamicsConstrains(max_deceleration=testinp[0],max_acceleration=testinp[1],max_speed=testinp[2])
    assert len(dyncon.get_attributes()) == results
    prettyprint(dyncon)
    dyncon2 = OSC.DynamicsConstrains(max_deceleration=testinp[0],max_acceleration=testinp[1],max_speed=testinp[2])
    dyncon3 = OSC.DynamicsConstrains(max_deceleration=testinp[0],max_acceleration=testinp[1],max_speed=50)
    assert dyncon == dyncon2
    assert dyncon != dyncon3

@pytest.mark.parametrize("testinp,results",[([None,None,None],False),([1,None,None],True),([1,None,2],True),([1,2,4],True) ] )
def test_dynamics_constraints_filled(testinp,results):
    dyncon = OSC.DynamicsConstrains(max_deceleration=testinp[0],max_acceleration=testinp[1],max_speed=testinp[2])

    assert dyncon.is_filled() == results


@pytest.mark.parametrize("testinp,results",[([None,None,None,None],0),([1,None,None,None],1),([1,None,None,OSC.ReferenceContext.relative],2),([1,2,4,None],3),([1,2,4,OSC.ReferenceContext.absolute],4) ] )
def test_orientation(testinp,results):
    orientation = OSC.Orientation(h=testinp[0],p=testinp[1],r=testinp[2],reference=testinp[3])
    prettyprint(orientation)
    assert len(orientation.get_attributes()) == results
    orientation2 = OSC.Orientation(h=testinp[0],p=testinp[1],r=testinp[2],reference=testinp[3])
    orientation3 = OSC.Orientation(h=10,p=testinp[1],r=testinp[2],reference=testinp[3])
    assert orientation == orientation2
    assert orientation != orientation3

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
    param2 = OSC.Parameter('stuffs',OSC.ParameterType.integer,'1')
    param3 = OSC.Parameter('stuffs',OSC.ParameterType.integer,'2')
    assert param == param2
    assert param != param3

def test_catalogreference():
    catref = OSC.CatalogReference('VehicleCatalog','S60')
    prettyprint(catref.get_element())
    catref.add_parameter_assignment('stuffs',1)
    prettyprint(catref.get_element())
    
    catref2 = OSC.CatalogReference('VehicleCatalog','S60')
    catref2.add_parameter_assignment('stuffs',1)
    
    catref3 = OSC.CatalogReference('VehicleCatalog','S60')
    catref3.add_parameter_assignment('stuffs',2)

    assert catref == catref2
    assert catref != catref3

def test_waypoint():
    wp = OSC.Waypoint(OSC.WorldPosition(),OSC.RouteStrategy.shortest)
    prettyprint(wp.get_element())
    wp2 = OSC.Waypoint(OSC.WorldPosition(),OSC.RouteStrategy.shortest)
    wp3 = OSC.Waypoint(OSC.WorldPosition(1),OSC.RouteStrategy.shortest)
    assert wp == wp2
    assert wp != wp3


def test_route():
    route = OSC.Route('myroute')
    route.add_waypoint(OSC.WorldPosition(0,0,0,0,0,0),OSC.RouteStrategy.shortest)
    route.add_waypoint(OSC.WorldPosition(1,1,0,0,0,0),OSC.RouteStrategy.shortest)

    prettyprint(route.get_element())

    route2 = OSC.Route('myroute')
    route2.add_waypoint(OSC.WorldPosition(0,0,0,0,0,0),OSC.RouteStrategy.shortest)
    route2.add_waypoint(OSC.WorldPosition(1,1,0,0,0,0),OSC.RouteStrategy.shortest)

    route3 = OSC.Route('myroute')
    route3.add_waypoint(OSC.WorldPosition(0,1,0,0,0,0),OSC.RouteStrategy.shortest)
    route3.add_waypoint(OSC.WorldPosition(1,1,0,0,0,0),OSC.RouteStrategy.shortest)

    assert route == route2
    assert route != route3

def test_paramdeclaration():
    
    pardec = OSC.ParameterDeclarations()
    pardec.add_parameter(OSC.Parameter('myparam1',OSC.ParameterType.integer,'1'))
    pardec.add_parameter(OSC.Parameter('myparam1',OSC.ParameterType.double,'0.01'))
    prettyprint(pardec.get_element())

def test_parameterassignment():
    parass = OSC.ParameterAssignment('param1',1)
    prettyprint(parass.get_element())
    parass2 = OSC.ParameterAssignment('param1',1)
    parass3 = OSC.ParameterAssignment('param1',2)
    assert parass == parass2
    assert parass != parass3

def test_properties():
    prop = OSC.Properties()
    prop.add_property('mything','2')
    prop.add_property('theotherthing','true')
    prettyprint(prop)
    prop2 = OSC.Properties()
    prop2.add_property('mything','2')
    prop2.add_property('theotherthing','true')
    
    prop3 = OSC.Properties()
    prop3.add_property('mything','2')
    prop3.add_property('theotherthin','true')
    assert prop == prop2
    assert prop != prop3
    

def test_controller():
    prop = OSC.Properties()
    prop.add_property('mything','2')
    prop.add_property('theotherthing','true')

    cnt = OSC.Controller('mycontroler',prop)
    prettyprint(cnt.get_element())
    cnt2 = OSC.Controller('mycontroler',prop)
    cnt3 = OSC.Controller('mycontroler3',prop)
    assert cnt == cnt2
    assert cnt != cnt3

def test_fileheader():
    fh = OSC.FileHeader('my_scenario','Mandolin')
    prettyprint(fh.get_element())
    fh2 = OSC.FileHeader('my_scenario','Mandolin')
    fh3 = OSC.FileHeader('my_scenario','Mandolin2')
    assert fh == fh2
    assert fh != fh3
def test_polyline():
    positionlist = []
    positionlist.append(OSC.RelativeLanePosition(ds=10,lane_id=-3,entity='Ego'))
    positionlist.append(OSC.RelativeLanePosition(dsLane=10,lane_id=-3,entity='Ego'))
    positionlist.append(OSC.RelativeLanePosition(ds=10,lane_id=-3,entity='Ego'))
    positionlist.append(OSC.RelativeLanePosition(ds=10,lane_id=-3,entity='Ego'))
    prettyprint(positionlist[0].get_element())
    polyline = OSC.Polyline([0,0.5,1,1.5],positionlist)
    prettyprint(polyline.get_element())
    polyline2 = OSC.Polyline([0,0.5,1,1.5],positionlist)
    polyline3 = OSC.Polyline([0,0.5,1,1.3],positionlist)
    assert polyline == polyline2
    assert polyline != polyline3

    polyline4 = OSC.Polyline([],positionlist)
    prettyprint(polyline4)


def test_clothoid():
    clot = OSC.Clothoid(1,0.1,10,OSC.WorldPosition(),0,1)
    prettyprint(clot.get_element())
    clot2 = OSC.Clothoid(1,0.1,10,OSC.WorldPosition(),0,1)
    clot3 = OSC.Clothoid(1,0.1,10,OSC.WorldPosition())
    prettyprint(clot3.get_element())
    assert clot == clot2
    assert clot != clot3

def test_trajectory():
    positionlist = []
    # positionlist.append(OSC.RelativeLanePosition(10,0.5,-3,'Ego'))
    # positionlist.append(OSC.RelativeLanePosition(10,1,-3,'Ego'))

    positionlist.append(OSC.WorldPosition())
    positionlist.append(OSC.WorldPosition(1))
    prettyprint(positionlist[0].get_element())
    polyline = OSC.Polyline([0,0.5],positionlist)
    traj = OSC.Trajectory('my_trajectory',False)
    traj.add_shape(polyline)
    prettyprint(traj.get_element())
    traj2 = OSC.Trajectory('my_trajectory',False)
    traj2.add_shape(polyline)
    traj3 = OSC.Trajectory('my_trajectory2',False)
    assert traj == traj2
    assert traj != traj3

def test_timeref():
    timeref = OSC.TimeReference(OSC.ReferenceContext.absolute,1,2)
    prettyprint(timeref.get_element())
    timeref2 = OSC.TimeReference(OSC.ReferenceContext.absolute,1,2)
    timeref3 = OSC.TimeReference(OSC.ReferenceContext.absolute,1,3)
    assert timeref == timeref2
    assert timeref != timeref3

def test_phase():
    p1 = OSC.Phase('myphase',1)
    prettyprint(p1.get_element())
    p1.add_signal_state('myid','red')
    p1.add_signal_state('myid','green')
    prettyprint(p1.get_element())
    p2 = OSC.Phase('myphase',1)
    p2.add_signal_state('myid','red')
    p2.add_signal_state('myid','green')
    
    p3 = OSC.Phase('myphase',1)
    p3.add_signal_state('myid','red')
    
    assert p1 == p2
    assert p1 != p3

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
    tsc2 = OSC.TrafficSignalController('my trafficlights')
    tsc2.add_phase(p1)
    tsc2.add_phase(p2)

    tsc3 = OSC.TrafficSignalController('my trafficlights3')
    tsc3.add_phase(p1)
    tsc3.add_phase(p2)
    assert tsc == tsc2
    assert tsc != tsc3

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

    traffic2 = OSC.TrafficDefinition('my traffic')
    traffic2.add_controller(controller,0.5)
    traffic2.add_controller(OSC.CatalogReference('ControllerCatalog','my controller'),0.5)
    traffic2.add_vehicle(OSC.VehicleCategory.car,0.9)
    traffic2.add_vehicle(OSC.VehicleCategory.bicycle,0.1)

    traffic3 = OSC.TrafficDefinition('my traffic')
    traffic3.add_controller(controller,0.5)
    traffic3.add_vehicle(OSC.VehicleCategory.car,0.9)
    assert traffic == traffic2
    assert traffic != traffic3


def test_weather():
    weather = OSC.Weather(OSC.CloudState.free,100,0)
    prettyprint(weather.get_element())
    weather2 = OSC.Weather(OSC.CloudState.free,100,0)
    weather3 = OSC.Weather(OSC.CloudState.free,100,1)
    assert weather == weather2
    assert weather != weather3
    weather = OSC.Weather(sun = OSC.Sun(1,1,1))
    prettyprint(weather.get_element())

def test_tod():
    tod = OSC.TimeOfDay(True,2020,10,1,18,30,30)
    prettyprint(tod.get_element())
    tod2 = OSC.TimeOfDay(True,2020,10,1,18,30,30)
    tod3 = OSC.TimeOfDay(True,2020,10,1,18,30,31)
    assert tod == tod2
    assert tod != tod3

def test_roadcondition():
    rc = OSC.RoadCondition(1)
    prettyprint(rc.get_element())
    rc2 = OSC.RoadCondition(1)
    rc3 = OSC.RoadCondition(2)
    assert rc == rc2
    assert rc != rc3

def test_environment():
    tod = OSC.TimeOfDay(True,2020,10,1,18,30,30)
    weather = OSC.Weather(OSC.CloudState.free,100)

    rc = OSC.RoadCondition(1)

    env = OSC.Environment(tod,weather,rc)
    prettyprint(env.get_element())
    env2 = OSC.Environment(tod,weather,rc)
    env3 = OSC.Environment(tod,weather,OSC.RoadCondition(3))
    assert env == env2
    assert env != env3

def test_controlpoint():
    cp1 = OSC.ControlPoint(OSC.WorldPosition(),1,0.1)
    prettyprint(cp1)
    cp2 = OSC.ControlPoint(OSC.WorldPosition(),1,0.1)
    cp3 = OSC.ControlPoint(OSC.WorldPosition(),1,0.2)
    assert cp1 == cp2
    assert cp1 != cp3

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

    nurb2 = OSC.Nurbs(2)
    nurb2.add_control_point(cp1)
    nurb2.add_control_point(cp2)
    nurb2.add_control_point(cp3)
    nurb2.add_knots([5,4,3,2,1])

    nurb3 = OSC.Nurbs(2)
    nurb3.add_control_point(cp1)
    nurb3.add_control_point(cp2)
    nurb3.add_control_point(cp3)
    nurb3.add_knots([5,4,3,2,0.5])

def test_oscenum():
    enum1 = OSC.enumerations._OscEnum('classname','testname')
    assert enum1.get_name()=='testname'
    enum2 = OSC.enumerations._OscEnum('classname','testname',min_minor_version=2)
    with pytest.raises(OSC.OpenSCENARIOVersionError):
        enum2.get_name()
    enum3 = OSC.enumerations._OscEnum('classname','testname',max_minor_version=0)
    with pytest.raises(OSC.OpenSCENARIOVersionError):
        enum3.get_name()

def test_distancesteadystate():
    tdss = OSC.TargetDistanceSteadyState(1)
    tdss2 = OSC.TargetDistanceSteadyState(1)
    tdss3 = OSC.TargetDistanceSteadyState(12)
    assert tdss == tdss2
    assert tdss != tdss3
    prettyprint(tdss)

def test_timesteadystate():
    ttss = OSC.TargetTimeSteadyState(1)
    ttss2 = OSC.TargetTimeSteadyState(1)
    ttss3 = OSC.TargetTimeSteadyState(12)
    assert ttss == ttss2
    assert ttss != ttss3
    prettyprint(ttss)

def test_wind():
    w = OSC.Wind(0,1)
    w2 = OSC.Wind(0,1)
    w3 = OSC.Wind(1,1)
    assert w == w2
    assert w != w3
    prettyprint(w)

def test_precipitation():
    p = OSC.Precipitation(OSC.PrecipitationType.rain,1)
    p2 = OSC.Precipitation(OSC.PrecipitationType.rain,1)
    p3 = OSC.Precipitation(OSC.PrecipitationType.rain,2)
    assert p == p2
    assert p != p3
    prettyprint(p)

def test_sun():
    s = OSC.Sun(1,1,1)
    s2 = OSC.Sun(1,1,1)
    s3 = OSC.Sun(1,2,1)

    assert s == s2
    assert s != s3
    prettyprint(s)

def test_sun():
    s = OSC.Fog(1,OSC.BoundingBox(1,1,1,1,1,1))
    s2 = OSC.Fog(1,OSC.BoundingBox(1,1,1,1,1,1))
    s3 = OSC.Fog(2,OSC.BoundingBox(1,1,1,1,1,1))

    assert s == s2
    assert s != s3
    prettyprint(s)

def test_license():
    l = OSC.License('MPL-2')
    l2 = OSC.License('MPL-2')
    l3 = OSC.License('MIT')
    assert l == l2
    assert l != l3
    prettyprint(l)