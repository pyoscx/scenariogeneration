import pytest

import pyoscx as OSC

import xml.etree.ElementTree as ET


# TODO: add more tests here
def test_creating_new_catalog():
    cf = OSC.CatalogFile()


    cf.create_catalog('my_catalog.xml','VehicleCatalog','My first vehicle catalog','Mandolin')

    bb = OSC.BoundingBox(2,5,1.8,2.0,0,0.9)
    fa = OSC.Axle(30,0.8,1.68,2.98,0.4, name='FrontAxle')
    ba = OSC.Axle(30,0.8,1.68,0,0.4, name='RearAxle')
    white_veh = OSC.Vehicle('car_white',OSC.VehicleCategory.car,bb,fa,ba,69,10,10)

    white_veh.add_property_file('../models/car_white.osgb')
    white_veh.add_property('control','internal')
    white_veh.add_property('model_id','0')
    cf.add_to_catalog(white_veh)
    OSC.prettyprint(cf.catalog_element)
    # cf.dump()