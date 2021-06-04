"""
Test script to create a straight road with a signal at an arbitrary s-coordinate.
"""
from scenariogeneration import xodr as pyodrx
from scenariogeneration import prettyprint

def test_signal_validity():

    signal = pyodrx.Signal(s=98.0, t=-4, country="USA", Type="R1", subtype="1")
    signal.add_validity(1, 1)
    road = pyodrx.create_straight_road(0)
    road.add_signal(signal)
    prettyprint(road.get_element())

def test_object_validity():

    guardrail = pyodrx.Object(0,0,height=0.3,zOffset=0.4,Type=pyodrx.ObjectType.barrier,name="guardRail")
    guardrail.add_validity(1, 1)
    road = pyodrx.create_straight_road(0)
    road.add_object(guardrail)
    prettyprint(road.get_element())

def test_signal():
    signal1 = pyodrx.Signal(s=10.0, t=-2, dynamic=pyodrx.Dynamic.no, orientation=pyodrx.Orientation.positive, zOffset=0.00, country="US", Type="R1",
                            subtype="1")
    
    signal2 = pyodrx.Signal(s=20.0, t=-2, dynamic=pyodrx.Dynamic.no, orientation=pyodrx.Orientation.positive, country="DEU", Type="274",
                            subtype="120", value=120, unit="km/h") 
    
    road = pyodrx.create_straight_road(0)
    road.add_signal(signal1)
    road.add_signal(signal2)
    prettyprint(road.get_element())
    signal3 = pyodrx.Signal(s=10.0, t=-2, dynamic=pyodrx.Dynamic.no, orientation=pyodrx.Orientation.positive, zOffset=0.00, country="US", Type="R1",
                            subtype="1")
    # unique fixer
    signal3.id = signal1.id
    assert signal1 == signal3
    assert signal1 != signal2

def test_object():
    object1 = pyodrx.Object(s=10.0, t=-2, dynamic=pyodrx.Dynamic.no, orientation=pyodrx.Orientation.positive, zOffset=0.00, id="1", height=1.0, Type=pyodrx.ObjectType.pole)
    
    #same chosen ID should cause warning and be resolved automatically
    object2 = pyodrx.Object(s=20.0, t=-2, dynamic=pyodrx.Dynamic.no, orientation=pyodrx.Orientation.positive, zOffset=0.00, height=10, id="1", Type=pyodrx.ObjectType.streetLamp) 
    
    road = pyodrx.create_straight_road(0)
    road.add_object([object1, object2])
    prettyprint(road.get_element())
    object3 = pyodrx.Object(s=10.0, t=-2, dynamic=pyodrx.Dynamic.no, orientation=pyodrx.Orientation.positive, zOffset=0.00, id="1", height=1.0, Type=pyodrx.ObjectType.pole)
    object3.id = object1.id
    assert object1 == object3
    assert object2 != object1
    
def test_repeated_object():
    object1 = pyodrx.Object(s=10.0, t=-2, dynamic=pyodrx.Dynamic.no, orientation=pyodrx.Orientation.positive, zOffset=0.00, height=1.0, Type=pyodrx.ObjectType.pole)
    object1.repeat(100,50)
    road = pyodrx.create_straight_road(0)
    road.add_object(object1)
    prettyprint(road.get_element())
    
    object2 = pyodrx.Object(s=10.0, t=-2, dynamic=pyodrx.Dynamic.no, orientation=pyodrx.Orientation.positive, zOffset=0.00, height=1.0, Type=pyodrx.ObjectType.pole)
    object2.repeat(100,50)

    object3 = pyodrx.Object(s=10.0, t=-2, dynamic=pyodrx.Dynamic.no, orientation=pyodrx.Orientation.positive, zOffset=0.00, height=1.0, Type=pyodrx.ObjectType.pole)
    object3.repeat(100,50)

    object3.id = object1.id
    assert object1 == object3
    assert object2 != object1

def test_object_roadside():
    road = pyodrx.create_straight_road(0)
    odr = pyodrx.OpenDrive('myroad')
    odr.add_road(road)
    odr.adjust_roads_and_lanes()
    object1 = pyodrx.Object(s=0, t=0, dynamic=pyodrx.Dynamic.no, orientation=pyodrx.Orientation.positive, zOffset=0.00, height=1.0, Type=pyodrx.ObjectType.pole)
    road.add_object_roadside(object1,50,tOffset=0.85)
    prettyprint(road.get_element())  