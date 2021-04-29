import pytest

import os
from scenariogeneration import xosc as OSC
from scenariogeneration import prettyprint
import xml.etree.ElementTree as ET


# TODO: add more tests here
def test_creating_new_catalog():
    cf = OSC.CatalogFile()


    cf.create_catalog('my_catalog.xml','VehicleCatalog','My first vehicle catalog','Mandolin')

    bb = OSC.BoundingBox(2,5,1.8,2.0,0,0.9)
    fa = OSC.Axle(0.523598775598,0.8,1.68,2.98,0.4)
    ba = OSC.Axle(0.523598775598,0.8,1.68,0,0.4)
    white_veh = OSC.Vehicle('car_white',OSC.VehicleCategory.car,bb,fa,ba,69,10,10)

    white_veh.add_property_file('../models/car_white.osgb')
    white_veh.add_property('control','internal')
    white_veh.add_property('model_id','0')
    cf.add_to_catalog(white_veh)
    prettyprint(cf.catalog_element)
    # cf.dump()

def test_catalog_reader_vehicle(tmpdir):
    
    tmpcatalog = os.path.join(tmpdir,'my_catalog.xosc')
    cf = OSC.CatalogFile()
    cf.create_catalog(tmpcatalog,'VehicleCatalog','My first vehicle catalog','Mandolin')

    bb = OSC.BoundingBox(2,5,1.8,2.0,0,0.9)
    fa = OSC.Axle(0.523598775598,0.8,1.68,2.98,0.4)
    ba = OSC.Axle(0.523598775598,0.8,1.68,0,0.4)
    white_veh = OSC.Vehicle('car_white',OSC.VehicleCategory.car,bb,fa,ba,69,10,10)

    white_veh.add_property_file('../models/car_white.osgb')
    white_veh.add_property('control','internal')
    white_veh.add_property('model_id','0')
    cf.add_to_catalog(white_veh)
    cf.dump()
    veh = OSC.CatalogReader(OSC.CatalogReference('my_catalog','car_white'),tmpdir)

    assert veh.boundingbox.boundingbox.height == white_veh.boundingbox.boundingbox.height
    assert veh.boundingbox.center.x == white_veh.boundingbox.center.x
    assert veh.name == white_veh.name
    


def test_catalog_reader_pedestrian(tmpdir):
    
    tmpcatalog = os.path.join(tmpdir,'my_catalog.xosc')
    cf = OSC.CatalogFile()
    cf.create_catalog(tmpcatalog,'PedestrianCatalog','My first vehicle catalog','Mandolin')

    bb = OSC.BoundingBox(2,5,1.8,2.0,0,0.9)

    peddler = OSC.Pedestrian('dude','dude-model',80,OSC.PedestrianCategory.pedestrian,bb)

    peddler.add_property_file('../models/car_white.osgb')
    cf.add_to_catalog(peddler)
    cf.dump()
    ped = OSC.CatalogReader(OSC.CatalogReference('my_catalog','dude'),tmpdir)
    print(ped.boundingbox.boundingbox.height)
    print(peddler.boundingbox.boundingbox.height)
    assert ped.boundingbox.boundingbox.height == peddler.boundingbox.boundingbox.height
    assert ped.boundingbox.center.x == peddler.boundingbox.center.x
    assert ped.mass == peddler.mass
    assert ped.name == peddler.name