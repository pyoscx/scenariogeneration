"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.

"""
import pytest

import os
from scenariogeneration import xosc
from scenariogeneration import prettyprint
import xml.etree.ElementTree as ET


@pytest.fixture
def parameter_fixture():
    pvs = xosc.ParameterValueSet()
    pvs.add_parameter("myparam1", "1")
    dist = xosc.DeterministicMultiParameterDistribution()
    dist.add_value_set(pvs)

    det = xosc.Deterministic()
    det.add_multi_distribution(dist)

    pvd = xosc.ParameterValueDistribution(
        "my_parametrization", "Mandolin", "my_test.xosc", det
    )
    return pvd


@pytest.fixture
def catalog_fixture():

    # create a vehicle
    bb = xosc.BoundingBox(2, 5, 1.8, 2.0, 0, 0.9)
    fa = xosc.Axle(0.523598775598, 0.8, 1.68, 2.98, 0.4)
    ba = xosc.Axle(0.523598775598, 0.8, 1.68, 0, 0.4)
    white_veh = xosc.Vehicle(
        "car_pink", xosc.VehicleCategory.car, bb, fa, ba, 69, 10, 10
    )

    white_veh.add_property_file("../models/car_white.osgb")
    white_veh.add_property("control", "internal")
    white_veh.add_property("model_id", "0")

    # dump it and create a new catalog file
    white_veh.dump_to_catalog(
        "my_vehicles.xosc", "VehicleCatalog", "My vehicle catalog", "Mandolin"
    )

    # create a new vehicle
    bb = xosc.BoundingBox(2, 5.1, 1.9, 2.0, 0, 0.9)
    fa = xosc.Axle(0.523598775598, 0.8, 1.68, 2.98, 0.4)
    ba = xosc.Axle(0.523598775598, 0.8, 1.68, 0, 0.4)
    red_veh = xosc.Vehicle("car_pink", xosc.VehicleCategory.car, bb, fa, ba, 69, 10, 10)

    red_veh.add_property_file("../models/car_red.osgb")
    red_veh.add_property("control", "internal")
    red_veh.add_property("model_id", "0")
    return red_veh


@pytest.fixture
def osc_fixture():

    parameters = xosc.ParameterDeclarations()
    parameters.add_parameter(xosc.Parameter("param1", xosc.ParameterType.string, "hej"))
    parameters.add_parameter(xosc.Parameter("param2", xosc.ParameterType.integer, 1))
    parameters.add_parameter(xosc.Parameter("param3", xosc.ParameterType.boolean, True))
    catalog = xosc.Catalog()
    catalog.add_catalog("VehicleCatalog", "Catalogs/VehicleCatalogs")
    catalog.add_catalog("ControllerCatalog", "Catalogs/ControllerCatalogs")

    roadfile = "Databases/SampleDatabase.xodr"
    road = xosc.RoadNetwork(roadfile)

    bb = xosc.BoundingBox(2, 5, 1.5, 1.5, 0, 0.2)
    fa = xosc.Axle(2, 2, 2, 1, 1)
    ba = xosc.Axle(1, 1, 2, 1, 1)
    veh = xosc.Vehicle("mycar", xosc.VehicleCategory.car, bb, fa, ba, 150, 10, 10)

    entities = xosc.Entities()
    entities.add_scenario_object("Ego", veh)

    init = xosc.Init()
    egospeed = xosc.AbsoluteSpeedAction(
        10,
        xosc.TransitionDynamics(
            xosc.DynamicsShapes.step, xosc.DynamicsDimension.distance, 3
        ),
    )

    init.add_init_action("Ego", egospeed)
    init.add_init_action(
        "Ego", xosc.TeleportAction(xosc.WorldPosition(1, 2, 3, 0, 0, 0))
    )

    sb = xosc.StoryBoard(init)

    return xosc.Scenario(
        "myscenario",
        "Mandolin",
        parameters,
        entities=entities,
        storyboard=sb,
        roadnetwork=road,
        catalog=catalog,
    )


def test_catalog_reader_vehicle(tmpdir):

    tmpcatalog = os.path.join(tmpdir, "my_catalog.xosc")
    cf = xosc.CatalogFile()
    cf.create_catalog(
        tmpcatalog, "VehicleCatalog", "My first vehicle catalog", "Mandolin"
    )

    bb = xosc.BoundingBox(2, 5, 1.8, 2.0, 0, 0.9)
    fa = xosc.Axle(0.523598775598, 0.8, 1.68, 2.98, 0.4)
    ba = xosc.Axle(0.523598775598, 0.8, 1.68, 0, 0.4)
    orig = xosc.Vehicle("car_white", xosc.VehicleCategory.car, bb, fa, ba, 69, 10, 10)

    orig.add_property_file("../models/car_white.osgb")
    orig.add_property("control", "internal")
    orig.add_property("model_id", "0")
    orig.add_parameter(xosc.Parameter("asdf", xosc.ParameterType.string, "hej"))
    cf.add_to_catalog(orig)
    cf.dump()
    read = xosc.CatalogReader(xosc.CatalogReference("my_catalog", "car_white"), tmpdir)

    assert read == orig


def test_catalog_reader_pedestrian(tmpdir):

    tmpcatalog = os.path.join(tmpdir, "my_catalog.xosc")
    cf = xosc.CatalogFile()
    cf.create_catalog(
        tmpcatalog, "PedestrianCatalog", "My first vehicle catalog", "Mandolin"
    )

    bb = xosc.BoundingBox(2, 5, 1.8, 2.0, 0, 0.9)

    orig = xosc.Pedestrian(
        "dude", 80, xosc.PedestrianCategory.pedestrian, bb, "dude-model"
    )

    orig.add_property_file("../models/car_white.osgb")
    cf.add_to_catalog(orig)
    cf.dump()
    read = xosc.CatalogReader(xosc.CatalogReference("my_catalog", "dude"), tmpdir)
    assert read == orig


def test_misc_object_reader(tmpdir):
    tmpcatalog = os.path.join(tmpdir, "my_catalog.xosc")
    cf = xosc.CatalogFile()
    cf.create_catalog(
        tmpcatalog, "MiscObjectCatalog", "My first miscobject catalog", "Mandolin"
    )
    orig = xosc.MiscObject(
        "pole", 50, xosc.MiscObjectCategory.pole, xosc.BoundingBox(1, 1, 1, 1, 1, 1)
    )
    cf.add_to_catalog(orig)
    cf.dump()
    read = xosc.CatalogReader(xosc.CatalogReference("my_catalog", "pole"), tmpdir)
    assert read == orig


def test_maneuver_reader(tmpdir):
    tmpcatalog = os.path.join(tmpdir, "my_catalog.xosc")
    cf = xosc.CatalogFile()
    cf.create_catalog(
        tmpcatalog, "ManeuverCatalog", "My first miscobject catalog", "Mandolin"
    )
    event = xosc.Event("my_event", xosc.Priority.overwrite)
    event.add_action(
        "myaction",
        xosc.AbsoluteSpeedAction(
            19,
            xosc.TransitionDynamics(
                xosc.DynamicsShapes.linear, xosc.DynamicsDimension.rate, 3
            ),
        ),
    )
    event.add_trigger(
        xosc.EntityTrigger(
            "my_trigger",
            3,
            xosc.ConditionEdge.none,
            xosc.SpeedCondition(10, xosc.Rule.lessThan),
            "ego",
        )
    )
    orig = xosc.Maneuver("my_maneuver")
    orig.add_event(event)
    cf.add_to_catalog(orig)
    cf.dump()
    read = xosc.CatalogReader(
        xosc.CatalogReference("my_catalog", "my_maneuver"), tmpdir
    )
    assert read == orig


def test_route_reader(tmpdir):
    tmpcatalog = os.path.join(tmpdir, "my_catalog.xosc")
    cf = xosc.CatalogFile()
    cf.create_catalog(
        tmpcatalog, "RouteCatalog", "My first miscobject catalog", "Mandolin"
    )
    orig = xosc.Route("my_route")
    orig.add_waypoint(xosc.WorldPosition(), xosc.RouteStrategy.shortest)
    orig.add_waypoint(xosc.WorldPosition(1, 1, 1), xosc.RouteStrategy.fastest)
    cf.add_to_catalog(orig)
    cf.dump()
    read = xosc.CatalogReader(xosc.CatalogReference("my_catalog", "my_route"), tmpdir)
    assert read == orig


def test_environment_reader(tmpdir):
    tmpcatalog = os.path.join(tmpdir, "my_catalog.xosc")
    cf = xosc.CatalogFile()
    cf.create_catalog(
        tmpcatalog, "EnvironmentCatalog", "My first miscobject catalog", "Mandolin"
    )
    orig = xosc.Environment(
        "snow",
        weather=xosc.Weather(
            precipitation=xosc.Precipitation(xosc.PrecipitationType.snow, 10)
        ),
    )
    cf.add_to_catalog(orig)
    cf.dump()
    read = xosc.CatalogReader(xosc.CatalogReference("my_catalog", "snow"), tmpdir)
    assert read == orig


def test_trajectory_reader(tmpdir):
    tmpcatalog = os.path.join(tmpdir, "my_catalog.xosc")
    cf = xosc.CatalogFile()
    cf.create_catalog(
        tmpcatalog, "TrajectoryCatalog", "My first miscobject catalog", "Mandolin"
    )
    orig = xosc.Trajectory("my_trajectory", False)
    orig.add_shape(xosc.Clothoid(0.1, 0.01, 100, xosc.WorldPosition()))
    cf.add_to_catalog(orig)
    cf.dump()
    read = xosc.CatalogReader(
        xosc.CatalogReference("my_catalog", "my_trajectory"), tmpdir
    )
    assert read == orig


def test_controller_reader(tmpdir):
    tmpcatalog = os.path.join(tmpdir, "my_catalog.xosc")
    cf = xosc.CatalogFile()
    cf.create_catalog(
        tmpcatalog, "TrajectoryCatalog", "My first miscobject catalog", "Mandolin"
    )
    orig = xosc.Controller("my_controller", xosc.Properties())
    cf.add_to_catalog(orig)
    cf.dump()
    read = xosc.CatalogReader(
        xosc.CatalogReference("my_catalog", "my_controller"), tmpdir
    )
    assert read == orig


def test_parameter_reader(tmpdir, osc_fixture):
    tmpfile = os.path.join(tmpdir, "myscenario.xosc")
    osc_fixture.write_xml(tmpfile)
    read_params = xosc.ParameterDeclarationReader(tmpfile)

    assert osc_fixture.parameters == read_params


def test_osc_reader_scenario(tmpdir, osc_fixture):
    tmpfile = os.path.join(tmpdir, "myscenario.xosc")
    osc_fixture.write_xml(tmpfile)
    scenario = xosc.ParseOpenScenario(tmpfile)
    prettyprint(osc_fixture)
    assert osc_fixture == scenario


def test_osc_reader_catalog(tmpdir):
    tmpcatalog = os.path.join(tmpdir, "my_catalog.xosc")
    cf = xosc.CatalogFile()
    cf.create_catalog(
        tmpcatalog, "TrajectoryCatalog", "My first miscobject catalog", "Mandolin"
    )
    orig = xosc.Controller("my_controller", xosc.Properties())
    cf.add_to_catalog(orig)
    cf.dump()
    loader = xosc.CatalogLoader()
    loader.load_catalog("my_catalog", tmpdir)
    catref = xosc.CatalogReference("my_catalog", "my_controller")
    read = loader.parse(catref)
    assert read == orig

    secondloader = xosc.CatalogLoader()
    secondloader.load_catalog(catref, tmpdir)
    read = secondloader.parse(catref)
    assert read == orig


def test_catalog_loader(tmpdir):
    tmpcatalog = os.path.join(tmpdir, "my_catalog.xosc")
    cf = xosc.CatalogFile()
    cf.create_catalog(
        tmpcatalog, "TrajectoryCatalog", "My first miscobject catalog", "Mandolin"
    )
    orig = xosc.Controller("my_controller", xosc.Properties())
    cf.add_to_catalog(orig)
    cf.dump()
    read = xosc.CatalogReader(
        xosc.CatalogReference("my_catalog", "my_controller"), tmpdir
    )
    assert read == orig


def test_osc_reader_parameter(tmpdir, parameter_fixture):
    tmpfile = os.path.join(tmpdir, "myscenario.xosc")
    parameter_fixture.write_xml(tmpfile)
    scenario = xosc.ParseOpenScenario(tmpfile)
    prettyprint(parameter_fixture)
    prettyprint(scenario)
    assert parameter_fixture == scenario
