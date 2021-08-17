import pytest

import os
from scenariogeneration import xosc
from scenariogeneration import prettyprint
import xml.etree.ElementTree as ET



@pytest.fixture
def osc_fixture():

    parameters = xosc.ParameterDeclarations()
    parameters.add_parameter(xosc.Parameter('param1',xosc.ParameterType.string,'hej'))
    parameters.add_parameter(xosc.Parameter('param2',xosc.ParameterType.integer,1))
    parameters.add_parameter(xosc.Parameter('param3',xosc.ParameterType.boolean,True))
    catalog = xosc.Catalog()
    catalog.add_catalog('VehicleCatalog','Catalogs/VehicleCatalogs')
    catalog.add_catalog('ControllerCatalog','Catalogs/ControllerCatalogs')

    roadfile = 'Databases/SampleDatabase.xodr'
    road = xosc.RoadNetwork(roadfile)

    bb = xosc.BoundingBox(2,5,1.5,1.5,0,0.2)
    fa = xosc.Axle(2,2,2,1,1)
    ba = xosc.Axle(1,1,2,1,1)
    veh = xosc.Vehicle('mycar',xosc.VehicleCategory.car,bb,fa,ba,150,10,10)

    entities = xosc.Entities()
    entities.add_scenario_object('Ego',veh)

    init = xosc.Init()
    egospeed = xosc.AbsoluteSpeedAction(10,xosc.TransitionDynamics(xosc.DynamicsShapes.step,xosc.DynamicsDimension.distance,3))

    init.add_init_action('Ego',egospeed)
    init.add_init_action('Ego',xosc.TeleportAction(xosc.WorldPosition(1,2,3,0,0,0)))

    sb = xosc.StoryBoard(init)

    return xosc.Scenario('myscenario','Mandolin',parameters,entities=entities,storyboard = sb,roadnetwork=road,catalog=catalog)

def test_catalog_reader_vehicle(tmpdir):
    
    tmpcatalog = os.path.join(tmpdir,'my_catalog.xosc')
    cf = xosc.CatalogFile()
    cf.create_catalog(tmpcatalog,'VehicleCatalog','My first vehicle catalog','Mandolin')

    bb = xosc.BoundingBox(2,5,1.8,2.0,0,0.9)
    fa = xosc.Axle(0.523598775598,0.8,1.68,2.98,0.4)
    ba = xosc.Axle(0.523598775598,0.8,1.68,0,0.4)
    white_veh = xosc.Vehicle('car_white',xosc.VehicleCategory.car,bb,fa,ba,69,10,10)

    white_veh.add_property_file('../models/car_white.osgb')
    white_veh.add_property('control','internal')
    white_veh.add_property('model_id','0')
    white_veh.add_parameter(xosc.Parameter('asdf',xosc.ParameterType.string,'hej'))
    cf.add_to_catalog(white_veh)
    cf.dump()
    veh = xosc.CatalogReader(xosc.CatalogReference('my_catalog','car_white'),tmpdir)

    assert veh.boundingbox.boundingbox.height == white_veh.boundingbox.boundingbox.height
    assert veh.boundingbox.center.x == white_veh.boundingbox.center.x
    assert veh.name == white_veh.name
    


def test_catalog_reader_pedestrian(tmpdir):
    
    tmpcatalog = os.path.join(tmpdir,'my_catalog.xosc')
    cf = xosc.CatalogFile()
    cf.create_catalog(tmpcatalog,'PedestrianCatalog','My first vehicle catalog','Mandolin')

    bb = xosc.BoundingBox(2,5,1.8,2.0,0,0.9)

    peddler = xosc.Pedestrian('dude','dude-model',80,xosc.PedestrianCategory.pedestrian,bb)

    peddler.add_property_file('../models/car_white.osgb')
    cf.add_to_catalog(peddler)
    cf.dump()
    ped = xosc.CatalogReader(xosc.CatalogReference('my_catalog','dude'),tmpdir)

    assert ped.boundingbox.boundingbox.height == peddler.boundingbox.boundingbox.height
    assert ped.boundingbox.center.x == peddler.boundingbox.center.x
    assert ped.mass == peddler.mass
    assert ped.name == peddler.name
    assert ped.model == ped.model

def test_parameter_reader(tmpdir,osc_fixture):
    tmpfile = os.path.join(tmpdir,'myscenario.xosc')
    osc_fixture.write_xml(tmpfile)
    read_params = xosc.ParameterDeclarationReader(tmpfile)
    for i in range(3):
        assert osc_fixture.parameters.parameters[i].name == read_params.parameters[i].name
        assert osc_fixture.parameters.parameters[i].parameter_type == read_params.parameters[i].parameter_type
        assert osc_fixture.parameters.parameters[i].value == read_params.parameters[i].value
    
