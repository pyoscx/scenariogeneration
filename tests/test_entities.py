import pytest

import pyoscx as OSC


def test_properties():
    prop = OSC.Properties()
    prop.add_file('myprops.xml')
    OSC.prettyprint(prop.get_element())
    prop.add_property('mything','2')
    OSC.prettyprint(prop.get_element())
    prop.add_property('theotherthing','true')

def test_dimensions():
    dim = OSC.Dimensions(2,3,1.5)
    OSC.prettyprint(dim.get_element())

def test_center():
    cen = OSC.Center(1,0,0.3)
    OSC.prettyprint(cen.get_element())


def test_boundingbox():
    bb = OSC.BoundingBox(2.3,5,2,1,0,0.2)
    OSC.prettyprint(bb.get_element())


def test_axel():
    ba = OSC.Axel(1,1,2,1,1)
    OSC.prettyprint(ba.get_element())

def test_axels():
    fa = OSC.Axel(2,2,2,1,1)
    ba = OSC.Axel(1,1,2,1,1)
    aa = OSC.Axel(1,1,2,1,1)
    axels = OSC.Axels(fa,ba)
    axels.add_axel(aa)
    OSC.prettyprint(axels.get_element())

def test_vehicle():
    bb = OSC.BoundingBox(2,5,1.5,1.5,0,0.2)
    fa = OSC.Axel(2,2,2,1,1)
    ba = OSC.Axel(1,1,2,1,1)
    veh = OSC.Vehicle('mycar',OSC.VehicleCategory.car,bb,fa,ba,150,10,10)
    
    OSC.prettyprint(veh.get_element())
    veh.add_property_file('propfile.xml')
    veh.add_property('myprop','12')
    veh.add_axel(bb)
    param = OSC.Parameter('mypar',OSC.ParameterType.integer,'1')
    veh.add_parameter(param)
    
    OSC.prettyprint(veh.get_element())

def test_pedestrian():
    bb = OSC.BoundingBox(2,5,1.5,1.5,0,0.2)
    veh = OSC.Pedestrian('myped', 'ped', 100, OSC.PedestrianCategory.pedestrian, bb)
    
    OSC.prettyprint(veh.get_element())
    veh.add_property_file('propfile.xml')
    veh.add_property('myprop','12')
    param = OSC.Parameter('mypar',OSC.ParameterType.integer,'1')
    veh.add_parameter(param)
    
    OSC.prettyprint(veh.get_element())

def test_miscobj():
    bb = OSC.BoundingBox(2,5,1.5,1.5,0,0.2)
    veh = OSC.MiscObject('mycar',100,'obstacle',bb)
    
    OSC.prettyprint(veh.get_element())
    veh.add_property_file('propfile.xml')
    veh.add_property('myprop','12')
    param = OSC.Parameter('mypar',OSC.ParameterType.integer,'1')
    veh.add_parameter(param)
    OSC.prettyprint(veh.get_element())

def test_entity():
    ent = OSC.Entity('ego',object_type=OSC.ObjectType.vehicle)
    OSC.prettyprint(ent.get_element())
    ent = OSC.Entity('ego',entityref='Ego')
    OSC.prettyprint(ent.get_element())

def test_entities():
    bb = OSC.BoundingBox(2,5,1.5,1.5,0,0.2)
    fa = OSC.Axel(2,2,2,1,1)
    ba = OSC.Axel(1,1,2,1,1)
    veh = OSC.Vehicle('mycar',OSC.ObjectType.vehicle,bb,fa,ba,150,10,10)
    
    entities = OSC.Entities()
    entities.add_scenario_object('Ego',veh)
    entities.add_scenario_object('Target_1',veh)
    entities.add_entity_bytype('Target_2',OSC.ObjectType.vehicle)
    entities.add_entity_byref('Target_3','something')
    OSC.prettyprint(entities.get_element())

def test_controller():
    prop = OSC.Properties()
    prop.add_property('mything','2')
    prop.add_property('theotherthing','true')

    cnt = OSC.Controller('mycontroler',prop)
    OSC.prettyprint(cnt.get_element())

def test_controller_in_Entities():
    bb = OSC.BoundingBox(2,5,1.5,1.5,0,0.2)
    fa = OSC.Axel(2,2,2,1,1)
    ba = OSC.Axel(1,1,2,1,1)
    veh = OSC.Vehicle('mycar',OSC.ObjectType.vehicle,bb,fa,ba,150,10,10)

    prop = OSC.Properties()
    prop.add_property('mything','2')
    prop.add_property('theotherthing','true')

    cnt = OSC.Controller('mycontroler',prop)


    entities = OSC.Entities()
    entities.add_scenario_object('Ego',veh)
    entities.add_scenario_object('Target_1',veh,cnt)
    entities.add_entity_bytype('Target_2',OSC.ObjectType.vehicle)
    entities.add_entity_byref('Target_3','something')
    OSC.prettyprint(entities.get_element())


    
    OSC.prettyprint(veh.get_element())