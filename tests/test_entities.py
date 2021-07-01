import pytest

from scenariogeneration import xosc as OSC
from scenariogeneration import prettyprint

def test_properties():
    prop = OSC.Properties()
    prop.add_file('myprops.xml')
    prettyprint(prop.get_element())
    prop.add_property('mything','2')
    prettyprint(prop.get_element())
    prop.add_property('theotherthing','true')

    prop2 = OSC.Properties()
    prop2.add_file('myprops.xml')
    prop2.add_property('mything','2')
    prop2.add_property('theotherthing','true')

    prop3 = OSC.Properties()
    prop3.add_file('myprops.xml')

    assert prop == prop2
    assert prop != prop3

def test_dimensions():
    dim = OSC.Dimensions(2,3,1.5)
    prettyprint(dim.get_element())
    dim2 = OSC.Dimensions(2,3,1.5)
    dim3 = OSC.Dimensions(2,3,1.3)
    assert dim == dim2
    assert dim != dim3

def test_center():
    cen = OSC.Center(1,0,0.3)
    prettyprint(cen.get_element())
    cen2 = OSC.Center(1,0,0.3)
    cen3 = OSC.Center(1,0,0.2)
    assert cen == cen2
    assert cen != cen3

def test_boundingbox():
    bb = OSC.BoundingBox(2.3,5,2,1,0,0.2)
    prettyprint(bb.get_element())
    bb2 = OSC.BoundingBox(2.3,5,2,1,0,0.2)
    bb3 = OSC.BoundingBox(2.3,5,2,1,0,0.1)
    assert bb == bb2
    assert bb != bb3

def test_axel():
    ba = OSC.Axle(1,1,2,1,1)
    prettyprint(ba.get_element())
    ba2 = OSC.Axle(1,1,2,1,1)
    ba3 = OSC.Axle(1,1,2,1,12)
    assert ba == ba2
    assert ba != ba3

def test_axels():
    fa = OSC.Axle(2,2,2,1,1)
    ra = OSC.Axle(1,1,2,1,1)
    aa = OSC.Axle(1,1,2,1,1)
    axels = OSC.Axles(fa,ra)
    axels.add_axle(aa)
    prettyprint(axels.get_element())
    axels2 = OSC.Axles(fa,ra)
    axels2.add_axle(aa)
    axels3 = OSC.Axles(fa,ra)
    assert axels == axels2
    assert axels != axels3


def test_vehicle():
    bb = OSC.BoundingBox(2,5,1.5,1.5,0,0.2)
    fa = OSC.Axle(2,2,2,1,1)
    ba = OSC.Axle(1,1,2,1,1)
    
    veh = OSC.Vehicle('mycar',OSC.VehicleCategory.car,bb,fa,ba,150,10,10)
    
    prettyprint(veh.get_element())
    veh.add_property_file('propfile.xml')
    veh.add_property('myprop','12')
    veh.add_axle(ba)
    param = OSC.Parameter('mypar',OSC.ParameterType.integer,'1')
    veh.add_parameter(param)
    
    prettyprint(veh.get_element())

    veh2 = OSC.Vehicle('mycar',OSC.VehicleCategory.car,bb,fa,ba,150,10,10)
    veh2.add_property_file('propfile.xml')
    veh2.add_property('myprop','12')
    veh2.add_axle(ba)
    veh2.add_parameter(param)
    
    veh3 = OSC.Vehicle('mycar',OSC.VehicleCategory.car,bb,fa,ba,150,10,10)
    assert veh == veh2
    assert veh != veh3
    
def test_pedestrian():
    bb = OSC.BoundingBox(2,5,1.5,1.5,0,0.2)
    veh = OSC.Pedestrian('myped', 'ped', 100, OSC.PedestrianCategory.pedestrian, bb)
    
    prettyprint(veh.get_element())
    veh.add_property_file('propfile.xml')
    veh.add_property('myprop','12')
    param = OSC.Parameter('mypar',OSC.ParameterType.integer,'1')
    veh.add_parameter(param)
    
    prettyprint(veh.get_element())

    veh2 = OSC.Pedestrian('myped', 'ped', 100, OSC.PedestrianCategory.pedestrian, bb)
    veh2.add_property_file('propfile.xml')
    veh2.add_property('myprop','12')
    veh2.add_parameter(param)
    veh3 = OSC.Pedestrian('myped', 'ped', 100, OSC.PedestrianCategory.pedestrian, bb)

    assert veh == veh2
    assert veh != veh3

def test_miscobj():
    bb = OSC.BoundingBox(2,5,1.5,1.5,0,0.2)
    veh = OSC.MiscObject('mycar',100,OSC.MiscObjectCategory.obstacle,bb)
    
    prettyprint(veh.get_element())
    veh.add_property_file('propfile.xml')
    veh.add_property('myprop','12')
    param = OSC.Parameter('mypar',OSC.ParameterType.integer,'1')
    veh.add_parameter(param)
    prettyprint(veh.get_element())

    veh2 = OSC.MiscObject('mycar',100,OSC.MiscObjectCategory.obstacle,bb)
    veh2.add_property_file('propfile.xml')
    veh2.add_property('myprop','12')
    veh2.add_parameter(param)

    veh3 = OSC.MiscObject('mycar',100,OSC.MiscObjectCategory.obstacle,bb)

    assert veh == veh2
    assert veh != veh3
def test_entity():
    ent = OSC.Entity('ego',object_type=OSC.ObjectType.vehicle)
    prettyprint(ent.get_element())
    ent3 = OSC.Entity('ego',entityref='Ego')
    prettyprint(ent3.get_element())
    ent2 = OSC.Entity('ego',object_type=OSC.ObjectType.vehicle)
    assert ent == ent2
    assert ent != ent3

def test_entities():
    bb = OSC.BoundingBox(2,5,1.5,1.5,0,0.2)
    fa = OSC.Axle(2,2,2,1,1)
    ba = OSC.Axle(1,1,2,1,1)
    veh = OSC.Vehicle('mycar',OSC.VehicleCategory.car,bb,fa,ba,150,10,10)
    
    entities = OSC.Entities()
    entities.add_scenario_object('Ego',veh)
    entities.add_scenario_object('Target_1',veh)
    entities.add_entity_bytype('Target_2',OSC.ObjectType.vehicle)
    entities.add_entity_byref('Target_3','something')
    prettyprint(entities.get_element())

    entities2 = OSC.Entities()
    entities2.add_scenario_object('Ego',veh)
    entities2.add_scenario_object('Target_1',veh)
    entities2.add_entity_bytype('Target_2',OSC.ObjectType.vehicle)
    entities2.add_entity_byref('Target_3','something')

    entities3 = OSC.Entities()
    entities3.add_scenario_object('Ego',veh)
    entities3.add_scenario_object('Target_1',veh)
    entities3.add_entity_bytype('Target_2',OSC.ObjectType.vehicle)
    
    assert entities == entities2
    assert entities != entities3

def test_controller():
    prop = OSC.Properties()
    prop.add_property('mything','2')
    prop.add_property('theotherthing','true')

    cnt = OSC.Controller('mycontroler',prop)
    prettyprint(cnt.get_element())
    cnt2 = OSC.Controller('mycontroler',prop)
    cnt3 = OSC.Controller('mycontroler2',prop)
    assert cnt == cnt2
    assert cnt != cnt3

def test_controller_in_Entities():
    bb = OSC.BoundingBox(2,5,1.5,1.5,0,0.2)
    fa = OSC.Axle(2,2,2,1,1)
    ba = OSC.Axle(1,1,2,1,1)
    veh = OSC.Vehicle('mycar',OSC.VehicleCategory.car,bb,fa,ba,150,10,10)

    prop = OSC.Properties()
    prop.add_property('mything','2')
    prop.add_property('theotherthing','true')

    cnt = OSC.Controller('mycontroler',prop)


    entities = OSC.Entities()
    entities.add_scenario_object('Target_1',veh,cnt)

    prettyprint(entities.get_element())

    entities2 = OSC.Entities()
    entities2.add_scenario_object('Target_1',veh,cnt)

    entities3 = OSC.Entities()
    entities3.add_scenario_object('Target_2',veh,cnt)
    assert entities == entities2
    assert entities != entities3

def test_external_object():
    ext_obj = OSC.ExternalObjectReference('my object')
    ext_obj2 = OSC.ExternalObjectReference('my object')
    ext_obj3 = OSC.ExternalObjectReference('my object 2')

    assert ext_obj == ext_obj2
    assert ext_obj != ext_obj3
