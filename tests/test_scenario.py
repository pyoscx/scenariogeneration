
import pytest


import pyoscx as OSC



def test_catalog():

    catalog = OSC.Catalog()
    catalog.add_catalog('VehicleCatalog','Catalogs/VehicleCatalogs')
    catalog.add_catalog('ControllerCatalog','Catalogs/ControllerCatalogs')
    OSC.prettyprint(catalog.get_element())


def test_road():
    roadfile = 'Databases/SampleDatabase.xodr'
    road = OSC.RoadNetwork(roadfile)
    OSC.prettyprint(road.get_element())

def test_ScenarioObject():
    ent = OSC.ScenarioObject('Ego')
    ent.set_catalog_reference('VehicleCatalog','S90')
    ent.set_object_controller('ControllerCatalog','Default')
    OSC.prettyprint(ent.get_element())

def test_entity():
    ent = OSC.ScenarioObject('Vehicle')
    ent.set_catalog_reference('VehicleCatalog','S90')
    ent.set_object_controller('ControllerCatalog','Default')
    OSC.prettyprint(ent.get_element())



