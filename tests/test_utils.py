"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2022 The scenariogeneration Authors.

"""

import xml.etree.ElementTree as ET
import pytest
import datetime as dt
import os

from scenariogeneration import xosc as OSC
from scenariogeneration import prettyprint
from scenariogeneration.xosc.utils import _TrafficSignalState, ValueConstraintGroup

from .xml_validator import version_validation, ValidationResponse


@pytest.fixture(autouse=True)
def reset_version():
    OSC.enumerations.VersionBase().setVersion(minor=2)


def test_transition_dynamics():
    td = OSC.TransitionDynamics(
        OSC.DynamicsShapes.step, OSC.DynamicsDimension.distance, 1.0
    )
    assert len(td.get_attributes()) == 3

    prettyprint(td.get_element())

    td2 = OSC.TransitionDynamics(
        OSC.DynamicsShapes.step, OSC.DynamicsDimension.distance, 1
    )
    td3 = OSC.TransitionDynamics(
        OSC.DynamicsShapes.step,
        OSC.DynamicsDimension.distance,
        2,
        following_mode=OSC.FollowingMode.follow,
    )
    prettyprint(td2.get_element())
    prettyprint(td3.get_element())
    assert td == td2
    assert td != td3

    td4 = OSC.TransitionDynamics.parse(td.get_element())
    assert td == td4
    td5 = OSC.TransitionDynamics.parse(td3.get_element())
    assert td5 == td3
    assert version_validation("TransitionDynamics", td, 0) == ValidationResponse.OK
    assert version_validation("TransitionDynamics", td, 1) == ValidationResponse.OK
    assert version_validation("TransitionDynamics", td, 2) == ValidationResponse.OK
    with pytest.raises(ValueError):
        OSC.TransitionDynamics("dummy", OSC.DynamicsDimension.distance, 1.0)
    with pytest.raises(ValueError):
        OSC.TransitionDynamics(OSC.DynamicsShapes.step, "dummy", 1.0)


@pytest.mark.parametrize(
    "testinp,results",
    [([None, None, None], 0), ([1, None, None], 1), ([1, None, 2], 2), ([1, 2, 4], 3)],
)
def test_dynamics_constraints(testinp, results):
    dyncon = OSC.DynamicsConstraints(
        max_deceleration=testinp[0], max_acceleration=testinp[1], max_speed=testinp[2]
    )
    assert len(dyncon.get_attributes()) == results
    prettyprint(dyncon)
    dyncon2 = OSC.DynamicsConstraints(
        max_deceleration=testinp[0], max_acceleration=testinp[1], max_speed=testinp[2]
    )
    dyncon3 = OSC.DynamicsConstraints(
        max_deceleration=testinp[0],
        max_acceleration=testinp[1],
        max_speed=50,
        max_acceleration_rate=2,
        max_deceleration_rate=3,
    )
    assert dyncon == dyncon2
    assert dyncon != dyncon3
    assert version_validation("DynamicConstraints", dyncon, 0) == ValidationResponse.OK
    assert version_validation("DynamicConstraints", dyncon, 1) == ValidationResponse.OK
    assert version_validation("DynamicConstraints", dyncon, 2) == ValidationResponse.OK
    assert version_validation("DynamicConstraints", dyncon3, 2) == ValidationResponse.OK
    assert (
        version_validation("DynamicConstraints", dyncon3, 1)
        == ValidationResponse.OSC_VERSION
    )


@pytest.mark.parametrize(
    "testinp,results",
    [
        ([None, None, None], False),
        ([1, None, None], True),
        ([1, None, 2], True),
        ([1, 2, 4], True),
    ],
)
def test_dynamics_constraints_filled(testinp, results):
    dyncon = OSC.DynamicsConstraints(
        max_deceleration=testinp[0], max_acceleration=testinp[1], max_speed=testinp[2]
    )

    assert dyncon.is_filled() == results


@pytest.mark.parametrize(
    "testinp,results",
    [
        ([None, None, None, None], 0),
        ([1, None, None, None], 1),
        ([1, None, None, OSC.ReferenceContext.relative], 2),
        ([1, 2, 4, None], 3),
        ([1, 2, 4, OSC.ReferenceContext.absolute], 4),
    ],
)
def test_orientation(testinp, results):
    orientation = OSC.Orientation(
        h=testinp[0], p=testinp[1], r=testinp[2], reference=testinp[3]
    )
    prettyprint(orientation)
    assert len(orientation.get_attributes()) == results
    orientation2 = OSC.Orientation(
        h=testinp[0], p=testinp[1], r=testinp[2], reference=testinp[3]
    )
    orientation3 = OSC.Orientation(
        h=10, p=testinp[1], r=testinp[2], reference=testinp[3]
    )
    assert orientation == orientation2
    assert orientation != orientation3
    orientation4 = OSC.Orientation.parse(orientation.get_element())
    assert orientation == orientation4
    assert version_validation("Orientation", orientation, 0) == ValidationResponse.OK
    assert version_validation("Orientation", orientation, 1) == ValidationResponse.OK
    assert version_validation("Orientation", orientation, 2) == ValidationResponse.OK
    with pytest.raises(ValueError):
        OSC.Orientation(0, 0, 0, "dummy")


@pytest.mark.parametrize(
    "testinp,results",
    [
        ([None, None, None, None], False),
        ([1, None, None, None], True),
        ([1, None, None, OSC.ReferenceContext.relative], True),
        ([1, 2, 4, None], True),
        ([1, 2, 4, OSC.ReferenceContext.absolute], True),
    ],
)
def test_orientation_filled(testinp, results):
    dyncon = OSC.Orientation(
        h=testinp[0], p=testinp[1], r=testinp[2], reference=testinp[3]
    )

    assert dyncon.is_filled() == results


def test_parameter():
    param = OSC.Parameter("stuffs", OSC.ParameterType.double, "1.0")
    prettyprint(param.get_element())
    param2 = OSC.Parameter("stuffs", OSC.ParameterType.double, "1.0")
    param3 = OSC.Parameter("stuffs", OSC.ParameterType.double, "2.0")
    param4 = OSC.Parameter("stuffs", OSC.ParameterType.double, "1.0")
    assert param == param2
    assert param != param3
    param5 = OSC.Parameter.parse(param.get_element())
    assert param == param5
    vc = OSC.ValueConstraint(OSC.Rule.equalTo, "equalTo")
    vc2 = OSC.ValueConstraint(OSC.Rule.notEqualTo, "equalTo")
    vc3 = OSC.ValueConstraint(OSC.Rule.equalTo, "notEqualTo")

    vcg = ValueConstraintGroup()
    vcg2 = ValueConstraintGroup()
    vcg.add_value_constraint(vc)
    vcg.add_value_constraint(vc2)
    vcg2.add_value_constraint(vc2)
    vcg2.add_value_constraint(vc3)
    param4.add_value_constraint_group(vcg)
    param4.add_value_constraint_group(vcg2)
    prettyprint(param4.get_element())
    param6 = OSC.Parameter.parse(param4.get_element())
    assert param4 == param6

    assert version_validation("ParameterDeclaration", param, 0) == ValidationResponse.OK
    assert version_validation("ParameterDeclaration", param, 1) == ValidationResponse.OK
    assert version_validation("ParameterDeclaration", param, 2) == ValidationResponse.OK
    assert (
        version_validation("ParameterDeclaration", param4, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("ParameterDeclaration", param4, 2) == ValidationResponse.OK
    )
    with pytest.raises(ValueError):
        OSC.Parameter("stuffs", "dummt", "1.0")
    with pytest.raises(TypeError):
        param.add_value_constraint_group("dummy")


def test_variable():
    param = OSC.Variable("stuffs", OSC.ParameterType.string, "asdf")
    prettyprint(param.get_element())
    param2 = OSC.Variable("stuffs", OSC.ParameterType.string, "asdf")
    param3 = OSC.Variable("stuffs", OSC.ParameterType.boolean, "false")

    assert param == param2
    assert param != param3
    param5 = OSC.Variable.parse(param.get_element())
    assert param == param5

    assert (
        version_validation("VariableDeclaration", param, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("VariableDeclaration", param, 1)
        == ValidationResponse.OSC_VERSION
    )
    assert version_validation("VariableDeclaration", param, 2) == ValidationResponse.OK

    with pytest.raises(ValueError):
        OSC.Variable("stuff", "dummy", "1")


def test_catalogreference():
    catref = OSC.CatalogReference("VehicleCatalog", "S60")
    prettyprint(catref.get_element())
    catref.add_parameter_assignment("stuffs", 1)
    prettyprint(catref.get_element())

    catref2 = OSC.CatalogReference("VehicleCatalog", "S60")
    catref2.add_parameter_assignment("stuffs", 1)

    catref3 = OSC.CatalogReference("VehicleCatalog", "S60")
    catref3.add_parameter_assignment("stuffs", 2)

    assert catref == catref2
    assert catref != catref3

    catref.add_parameter_assignment("stuffs2", 5)
    catref4 = OSC.CatalogReference.parse(catref.get_element())
    prettyprint(catref.get_element())
    prettyprint(catref4.get_element())
    assert catref == catref4

    assert version_validation("CatalogReference", catref, 0) == ValidationResponse.OK
    assert version_validation("CatalogReference", catref, 1) == ValidationResponse.OK
    assert version_validation("CatalogReference", catref, 2) == ValidationResponse.OK


def test_paramdeclaration():
    pardec = OSC.ParameterDeclarations()
    pardec.add_parameter(OSC.Parameter("myparam1", OSC.ParameterType.boolean, "true"))
    pardec.add_parameter(OSC.Parameter("myparam1", OSC.ParameterType.double, "0.01"))
    pardec2 = OSC.ParameterDeclarations()
    pardec2.add_parameter(OSC.Parameter("myparam1", OSC.ParameterType.boolean, "true"))
    pardec2.add_parameter(OSC.Parameter("myparam1", OSC.ParameterType.double, "0.01"))
    pardec3 = OSC.ParameterDeclarations.parse(pardec.get_element())
    prettyprint(pardec.get_element())
    assert pardec == pardec2
    assert pardec == pardec3
    pardec4 = OSC.ParameterDeclarations()
    pardec4.add_parameter(OSC.Parameter("myparam2", OSC.ParameterType.int, "1"))
    pardec4.add_parameter(OSC.Parameter("myparam2", OSC.ParameterType.double, "0.01"))
    assert pardec4 != pardec

    assert (
        version_validation("ParameterDeclarations", pardec, 0) == ValidationResponse.OK
    )
    assert (
        version_validation("ParameterDeclarations", pardec, 1) == ValidationResponse.OK
    )
    assert (
        version_validation("ParameterDeclarations", pardec, 2) == ValidationResponse.OK
    )
    with pytest.raises(TypeError):
        pardec.add_parameter("dummy")


def test_variabledeclaration():
    pardec = OSC.VariableDeclarations()
    pardec.add_variable(OSC.Variable("myparam1", OSC.ParameterType.int, "1"))
    pardec.add_variable(OSC.Variable("myparam1", OSC.ParameterType.double, "0.01"))
    pardec2 = OSC.VariableDeclarations()
    pardec2.add_variable(OSC.Variable("myparam1", OSC.ParameterType.int, "1"))
    pardec2.add_variable(OSC.Variable("myparam1", OSC.ParameterType.double, "0.01"))
    pardec3 = OSC.VariableDeclarations.parse(pardec.get_element())
    prettyprint(pardec.get_element())
    assert pardec == pardec2
    assert pardec == pardec3
    pardec4 = OSC.VariableDeclarations()
    pardec4.add_variable(OSC.Variable("myparam2", OSC.ParameterType.int, "1"))
    pardec4.add_variable(OSC.Variable("myparam2", OSC.ParameterType.double, "0.01"))
    assert pardec4 != pardec

    assert (
        version_validation("VariableDeclarations", pardec, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("VariableDeclarations", pardec, 1)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("VariableDeclarations", pardec, 2) == ValidationResponse.OK
    )
    with pytest.raises(TypeError):
        pardec.add_variable("dummy")


def test_entityref():
    entref = OSC.EntityRef("ref_str")
    entref2 = OSC.EntityRef("ref_str")
    entref3 = OSC.EntityRef("ref_str2")
    prettyprint(entref.get_element())
    assert entref == entref2
    assert entref != entref3

    entref4 = OSC.EntityRef.parse(entref.get_element())
    assert entref == entref4

    assert version_validation("EntityRef", entref, 0) == ValidationResponse.OK
    assert version_validation("EntityRef", entref, 1) == ValidationResponse.OK
    assert version_validation("EntityRef", entref, 2) == ValidationResponse.OK


def test_parameterassignment():
    parass = OSC.ParameterAssignment("param1", 1)
    prettyprint(parass.get_element())
    parass2 = OSC.ParameterAssignment("param1", 1)
    parass3 = OSC.ParameterAssignment("param1", 2)
    assert parass == parass2
    assert parass != parass3

    parass4 = OSC.ParameterAssignment.parse(parass.get_element())
    assert parass4 == parass

    assert version_validation("ParameterAssignment", parass, 0) == ValidationResponse.OK
    assert version_validation("ParameterAssignment", parass, 1) == ValidationResponse.OK
    assert version_validation("ParameterAssignment", parass, 2) == ValidationResponse.OK


def test_boundinbox():
    bb = OSC.BoundingBox(1, 2, 1, 2, 3, 2)
    prettyprint(bb.get_element())
    bb2 = OSC.BoundingBox(1, 2, 1, 2, 3, 2)
    bb3 = OSC.BoundingBox(1, 3, 2, 3, 3, 2)
    assert bb == bb2
    assert bb != bb3
    bb4 = OSC.BoundingBox.parse(bb.get_element())
    assert bb4 == bb
    assert version_validation("BoundingBox", bb, 0) == ValidationResponse.OK
    assert version_validation("BoundingBox", bb, 1) == ValidationResponse.OK
    assert version_validation("BoundingBox", bb, 2) == ValidationResponse.OK


def test_center():
    cen = OSC.Center(1, 2, 3)
    prettyprint(cen.get_element())
    cen2 = OSC.Center(1, 2, 3)
    cen3 = OSC.Center(1, 2, 1)
    assert cen == cen2
    assert cen != cen3
    cen4 = OSC.Center.parse(cen.get_element())
    assert cen4 == cen
    assert version_validation("Center", cen, 0) == ValidationResponse.OK
    assert version_validation("Center", cen, 1) == ValidationResponse.OK
    assert version_validation("Center", cen, 2) == ValidationResponse.OK


def test_dimensions():
    dim = OSC.Dimensions(1, 2, 3)
    prettyprint(dim.get_element())
    dim2 = OSC.Dimensions(1, 2, 3)
    dim3 = OSC.Dimensions(1, 2, 1)
    assert dim == dim2
    assert dim != dim3
    dim4 = OSC.Dimensions.parse(dim.get_element())
    assert dim4 == dim
    assert version_validation("Dimensions", dim, 0) == ValidationResponse.OK
    assert version_validation("Dimensions", dim, 1) == ValidationResponse.OK
    assert version_validation("Dimensions", dim, 2) == ValidationResponse.OK


def test_properties():
    prop = OSC.Properties()
    prop.add_property("mything", "2")
    prop.add_property("theotherthing", "true")
    prop.add_file("propfile.xml")
    prettyprint(prop)
    prop2 = OSC.Properties()
    prop2.add_property("mything", "2")
    prop2.add_property("theotherthing", "true")
    prop2.add_file("propfile.xml")

    prop3 = OSC.Properties()
    prop3.add_property("mything", "2")
    prop3.add_property("theotherthin", "true")
    assert prop == prop2
    assert prop != prop3

    prop4 = OSC.Properties.parse(prop.get_element())
    assert prop4 == prop
    assert version_validation("Properties", prop, 0) == ValidationResponse.OK
    assert version_validation("Properties", prop, 1) == ValidationResponse.OK
    assert version_validation("Properties", prop, 2) == ValidationResponse.OK


def test_controller(tmpdir):
    prop = OSC.Properties()
    prop.add_property("mything", "2")
    prop.add_property("theotherthing", "true")

    param = OSC.Parameter("stuffs", OSC.ParameterType.int, "1")
    param2 = OSC.Parameter("stuffs2", OSC.ParameterType.double, "5")
    cnt = OSC.Controller(
        "mycontroler", prop, controller_type=OSC.ControllerType.appearance
    )
    prettyprint(cnt.get_element())
    cnt2 = OSC.Controller(
        "mycontroler", prop, controller_type=OSC.ControllerType.appearance
    )
    cnt3 = OSC.Controller("mycontroler3", prop)
    assert cnt == cnt2
    assert cnt != cnt3

    cnt.add_parameter(param)
    cnt.add_parameter(param2)
    prettyprint(cnt.get_element())
    cnt4 = OSC.Controller.parse(cnt.get_element())
    assert cnt4 == cnt
    assert version_validation("Controller", cnt3, 0) == ValidationResponse.OK
    assert version_validation("Controller", cnt3, 1) == ValidationResponse.OK
    assert version_validation("Controller", cnt, 2) == ValidationResponse.OK
    assert version_validation("Controller", cnt, 1) == ValidationResponse.OSC_VERSION
    cnt.dump_to_catalog(
        os.path.join(tmpdir, "my_catalog.xosc"),
        "ControllerCatalog",
        "test catalog",
        "Mandolin",
    )
    with pytest.raises(TypeError):
        OSC.Controller("mycontroler3", "dummy")
    with pytest.raises(ValueError):
        OSC.Controller("mycontroler3", prop, "dummy")


def test_fileheader():
    fh = OSC.FileHeader("my_scenario", "Mandolin", creation_date=dt.datetime.now())
    prettyprint(fh.get_element())
    fh2 = OSC.FileHeader("my_scenario", "Mandolin")
    props = OSC.Properties()
    props.add_file("dummy")
    fh3 = OSC.FileHeader("my_scenario", "Mandolin2", license=OSC.License("dummy"))

    assert fh == fh2
    assert fh != fh3

    fh4 = OSC.FileHeader.parse(fh.get_element())
    fh5 = OSC.FileHeader("my_scenario", "Mandolin2", properties=props)
    assert fh4 == fh
    assert version_validation("FileHeader", fh, 0) == ValidationResponse.OK
    assert version_validation("FileHeader", fh, 1) == ValidationResponse.OK
    assert version_validation("FileHeader", fh, 2) == ValidationResponse.OK

    assert version_validation("FileHeader", fh3, 0) == ValidationResponse.OSC_VERSION
    assert version_validation("FileHeader", fh3, 1) == ValidationResponse.OK
    assert version_validation("FileHeader", fh3, 2) == ValidationResponse.OK

    assert version_validation("FileHeader", fh5, 0) == ValidationResponse.OSC_VERSION
    assert version_validation("FileHeader", fh5, 1) == ValidationResponse.OSC_VERSION
    assert version_validation("FileHeader", fh5, 2) == ValidationResponse.OK


def test_timeref():
    timeref = OSC.TimeReference(OSC.ReferenceContext.absolute, 1, 2)
    prettyprint(timeref.get_element())
    timeref2 = OSC.TimeReference(OSC.ReferenceContext.absolute, 1, 2)
    timeref3 = OSC.TimeReference(OSC.ReferenceContext.absolute, 1, 3)
    assert timeref == timeref2
    assert timeref != timeref3

    timeref4 = OSC.TimeReference.parse(timeref.get_element())
    assert timeref4 == timeref
    assert version_validation("TimeReference", timeref, 0) == ValidationResponse.OK
    assert version_validation("TimeReference", timeref, 1) == ValidationResponse.OK
    assert version_validation("TimeReference", timeref, 2) == ValidationResponse.OK
    with pytest.raises(ValueError):
        OSC.TimeReference("dummy")


def test_phase():
    p1 = OSC.Phase("myphase", 1, traffic_group_state="hello")
    prettyprint(p1.get_element())
    p1.add_signal_state("myid", "red")
    p1.add_signal_state("myid", "green")
    prettyprint(p1.get_element())
    p2 = OSC.Phase("myphase", 1, traffic_group_state="hello")
    p2.add_signal_state("myid", "red")
    p2.add_signal_state("myid", "green")

    p3 = OSC.Phase("myphase", 1)
    p3.add_signal_state("myid", "red")

    assert p1 == p2
    assert p1 != p3

    p4 = OSC.Phase.parse(p1.get_element())
    assert p4 == p1

    assert version_validation("Phase", p1, 0) == ValidationResponse.OSC_VERSION
    assert version_validation("Phase", p1, 1) == ValidationResponse.OSC_VERSION
    assert version_validation("Phase", p1, 2) == ValidationResponse.OK
    assert version_validation("Phase", p3, 0) == ValidationResponse.OK
    assert version_validation("Phase", p3, 1) == ValidationResponse.OK


def test_TrafficSignalState():
    tss = _TrafficSignalState("ID_1", "Signal_State")
    tss2 = _TrafficSignalState("ID_1", "Signal_State")
    tss3 = _TrafficSignalState("ID_2", "Signal_State")
    prettyprint(tss.get_element())
    assert tss == tss2
    assert tss != tss3

    tss4 = _TrafficSignalState.parse(tss.get_element())
    assert tss4 == tss
    assert version_validation("TrafficSignalState", tss, 0) == ValidationResponse.OK
    assert version_validation("TrafficSignalState", tss, 1) == ValidationResponse.OK
    assert version_validation("TrafficSignalState", tss, 2) == ValidationResponse.OK


def test_TrafficSignalController():
    p1 = OSC.Phase("myphase", 1)
    p1.add_signal_state("myid", "red")
    p1.add_signal_state("myid", "green")

    p2 = OSC.Phase("myphase2", 3)
    p2.add_signal_state("myid2", "yellow")
    p2.add_signal_state("myid2", "green")
    p2.add_signal_state("myid2", "red")
    prettyprint(p2.get_element())

    tsc = OSC.TrafficSignalController("my trafficlights")
    tsc.add_phase(p1)
    tsc.add_phase(p2)
    prettyprint(tsc.get_element())
    tsc2 = OSC.TrafficSignalController("my trafficlights")
    tsc2.add_phase(p1)
    tsc2.add_phase(p2)

    tsc3 = OSC.TrafficSignalController("my trafficlights3")
    tsc3.add_phase(p1)
    tsc3.add_phase(p2)
    assert tsc == tsc2
    assert tsc != tsc3

    tsc4 = OSC.TrafficSignalController.parse(tsc.get_element())
    assert tsc4 == tsc

    assert (
        version_validation("TrafficSignalController", tsc, 0) == ValidationResponse.OK
    )
    assert (
        version_validation("TrafficSignalController", tsc, 1) == ValidationResponse.OK
    )
    assert (
        version_validation("TrafficSignalController", tsc, 2) == ValidationResponse.OK
    )


def test_trafficdefinition():
    prop = OSC.Properties()
    prop.add_file("mycontrollerfile.xml")
    controller = OSC.Controller("mycontroller", prop)

    traffic = OSC.TrafficDefinition("my traffic")
    traffic.add_controller(controller, 0.5)
    traffic.add_controller(
        OSC.CatalogReference("ControllerCatalog", "my controller"), 0.5
    )

    traffic.add_vehicle(OSC.VehicleCategory.car, 0.9)
    traffic.add_vehicle(OSC.VehicleCategory.bicycle, 0.1)

    prettyprint(traffic.get_element())

    traffic2 = OSC.TrafficDefinition("my traffic")
    traffic2.add_controller(controller, 0.5)
    traffic2.add_controller(
        OSC.CatalogReference("ControllerCatalog", "my controller"), 0.5
    )
    traffic2.add_vehicle(OSC.VehicleCategory.car, 0.9)
    traffic2.add_vehicle(OSC.VehicleCategory.bicycle, 0.1)

    traffic3 = OSC.TrafficDefinition("my traffic")
    traffic3.add_controller(controller, 0.5)
    traffic3.add_vehicle(OSC.VehicleCategory.car, 0.9)
    traffic3.add_vehicle_role(OSC.Role.military, 1)
    assert traffic == traffic2
    assert traffic != traffic3
    prettyprint(traffic3)
    traffic4 = OSC.TrafficDefinition.parse(traffic.get_element())
    assert traffic == traffic4

    traffic5 = OSC.TrafficDefinition.parse(traffic3.get_element())
    assert traffic3 == traffic5

    assert version_validation("TrafficDefinition", traffic, 0) == ValidationResponse.OK
    assert version_validation("TrafficDefinition", traffic, 1) == ValidationResponse.OK
    assert version_validation("TrafficDefinition", traffic, 2) == ValidationResponse.OK

    assert (
        version_validation("TrafficDefinition", traffic3, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("TrafficDefinition", traffic3, 1)
        == ValidationResponse.OSC_VERSION
    )
    assert version_validation("TrafficDefinition", traffic3, 2) == ValidationResponse.OK

    with pytest.raises(TypeError):
        traffic.add_controller("dummy", 1)
    with pytest.raises(ValueError):
        traffic.add_vehicle("dummy", 0.3)
    with pytest.raises(ValueError):
        traffic.add_vehicle_role("dummy", 1)


def test_weather():
    weather = OSC.Weather(
        OSC.FractionalCloudCover.fourOktas,
        100,
        0,
        dome_image="dome.jpg",
        dome_azimuth_offset=2,
    )
    prettyprint(weather.get_element())
    weather2 = OSC.Weather(
        OSC.FractionalCloudCover.fourOktas,
        100,
        0,
        dome_image="dome.jpg",
        dome_azimuth_offset=2,
    )
    weather3 = OSC.Weather(
        OSC.FractionalCloudCover.fourOktas,
        100,
        0,
        dome_image="dome.jpg",
        dome_azimuth_offset=3,
    )
    assert weather == weather2
    assert weather != weather3
    weather4 = OSC.Weather(
        OSC.CloudState.free,
        precipitation=OSC.Precipitation(OSC.PrecipitationType.rain, 3),
        fog=OSC.Fog(10, OSC.BoundingBox(1, 2, 3, 4, 5, 6)),
        sun=OSC.Sun(1, 1, 1),
    )

    weather6 = OSC.Weather.parse(weather.get_element())
    assert weather == weather6
    weather5 = OSC.Weather(OSC.CloudState.free, 100, 0, wind=OSC.Wind(0.3, 10))

    assert version_validation("Weather", weather, 0) == ValidationResponse.OSC_VERSION
    assert version_validation("Weather", weather, 1) == ValidationResponse.OSC_VERSION
    assert version_validation("Weather", weather, 2) == ValidationResponse.OK

    assert version_validation("Weather", weather4, 0) == ValidationResponse.OK
    assert version_validation("Weather", weather4, 1) == ValidationResponse.OK

    assert version_validation("Weather", weather5, 1) == ValidationResponse.OK
    assert version_validation("Weather", weather5, 0) == ValidationResponse.OSC_VERSION

    cloud_param = OSC.Weather("$asdf")
    cloud_param.setVersion(2)

    prettyprint(cloud_param.get_element())
    cloud_param2 = OSC.Weather.parse(cloud_param.get_element())
    assert cloud_param == cloud_param2
    with pytest.raises(ValueError):
        OSC.Weather(
            "dummy",
            precipitation=OSC.Precipitation(OSC.PrecipitationType.rain, 3),
            fog=OSC.Fog(10, OSC.BoundingBox(1, 2, 3, 4, 5, 6)),
            sun=OSC.Sun(1, 1, 1),
            wind=OSC.Wind(1, 3),
        )
    with pytest.raises(TypeError):
        OSC.Weather(
            OSC.CloudState.free,
            precipitation="dummy",
            fog=OSC.Fog(10, OSC.BoundingBox(1, 2, 3, 4, 5, 6)),
            sun=OSC.Sun(1, 1, 1),
            wind=OSC.Wind(1, 3),
        )
    with pytest.raises(TypeError):
        OSC.Weather(
            OSC.CloudState.free,
            precipitation=OSC.Precipitation(OSC.PrecipitationType.rain, 3),
            fog="dummy",
            sun=OSC.Sun(1, 1, 1),
            wind=OSC.Wind(1, 3),
        )
    with pytest.raises(TypeError):
        OSC.Weather(
            OSC.CloudState.free,
            precipitation=OSC.Precipitation(OSC.PrecipitationType.rain, 3),
            fog=OSC.Fog(10, OSC.BoundingBox(1, 2, 3, 4, 5, 6)),
            sun="dummy",
            wind=OSC.Wind(1, 3),
        )
    with pytest.raises(TypeError):
        OSC.Weather(
            OSC.CloudState.free,
            precipitation=OSC.Precipitation(OSC.PrecipitationType.rain, 3),
            fog=OSC.Fog(10, OSC.BoundingBox(1, 2, 3, 4, 5, 6)),
            sun=OSC.Sun(1, 1, 1),
            wind="dummy",
        )


def test_tod():
    tod = OSC.TimeOfDay(True, 2020, 10, 1, 18, 30, 30)
    prettyprint(tod.get_element())
    tod2 = OSC.TimeOfDay(True, 2020, 10, 1, 18, 30, 30)
    tod3 = OSC.TimeOfDay(True, 2020, 10, 1, 18, 30, 31)
    assert tod == tod2
    assert tod != tod3

    tod4 = OSC.TimeOfDay.parse(tod.get_element())
    prettyprint(tod4.get_element())
    assert tod4 == tod

    assert version_validation("TimeOfDay", tod, 0) == ValidationResponse.OK
    assert version_validation("TimeOfDay", tod, 1) == ValidationResponse.OK
    assert version_validation("TimeOfDay", tod, 2) == ValidationResponse.OK


def test_roadcondition():
    prop = OSC.Properties()
    prop.add_property("mything", "2")
    prop.add_property("theotherthing", "true")
    prop.add_file("propfile.xml")
    rc = OSC.RoadCondition(1, prop, OSC.Wetness.highFlooded)
    prettyprint(rc.get_element())
    rc2 = OSC.RoadCondition(1, prop, OSC.Wetness.highFlooded)
    rc3 = OSC.RoadCondition(2)
    assert rc == rc2
    assert rc != rc3

    rc4 = OSC.RoadCondition.parse(rc.get_element())
    prettyprint(rc4.get_element())

    assert rc == rc4

    assert version_validation("RoadCondition", rc, 0) == ValidationResponse.OSC_VERSION
    assert version_validation("RoadCondition", rc, 1) == ValidationResponse.OSC_VERSION
    assert version_validation("RoadCondition", rc, 2) == ValidationResponse.OK
    assert version_validation("RoadCondition", rc3, 0) == ValidationResponse.OK
    assert version_validation("RoadCondition", rc3, 1) == ValidationResponse.OK

    with pytest.raises(TypeError):
        OSC.RoadCondition(1, "dummy")
    with pytest.raises(ValueError):
        OSC.RoadCondition(1, None, "dummy")


def test_environment(tmpdir):
    tod = OSC.TimeOfDay(True, 2020, 10, 1, 18, 30, 30)
    fog = OSC.Fog(10, OSC.BoundingBox(1, 2, 3, 4, 5, 6))
    weather = OSC.Weather(OSC.FractionalCloudCover.oneOktas, 100, fog=fog)
    weather2 = OSC.Weather(
        OSC.CloudState.free,
        precipitation=OSC.Precipitation(OSC.PrecipitationType.rain, 3),
        fog=fog,
        sun=OSC.Sun(1, 1, 1),
    )

    rc = OSC.RoadCondition(1)

    env = OSC.Environment("Env_name1", tod, weather, roadcondition=rc)
    prettyprint(env.get_element(), None)
    env2 = OSC.Environment("Env_name1", tod, weather, roadcondition=rc)
    env3 = OSC.Environment("Env_name2", tod, weather, OSC.RoadCondition(3))
    assert env == env2
    assert env != env3

    env4 = OSC.Environment.parse(env.get_element())
    prettyprint(env4.get_element())
    assert env4 == env
    env5 = OSC.Environment("Env_name2", tod, weather2, OSC.RoadCondition(3))
    env6 = OSC.Environment("Env_name2", roadcondition=OSC.RoadCondition(3))

    assert version_validation("Environment", env, 0) == ValidationResponse.OSC_VERSION
    assert version_validation("Environment", env, 1) == ValidationResponse.OSC_VERSION
    assert version_validation("Environment", env, 2) == ValidationResponse.OK
    assert version_validation("Environment", env5, 0) == ValidationResponse.OK
    assert version_validation("Environment", env6, 1) == ValidationResponse.OK
    env.dump_to_catalog(
        os.path.join(tmpdir, "my_catalog.xosc"),
        "EnvironmentCatalog",
        "test catalog",
        "Mandolin",
    )

    with pytest.raises(TypeError):
        OSC.Environment("Env_name1", "dummy", weather, roadcondition=rc)
    with pytest.raises(TypeError):
        OSC.Environment("Env_name1", tod, "dummy", roadcondition=rc)
    with pytest.raises(TypeError):
        OSC.Environment("Env_name1", tod, weather, roadcondition="dummy")
    with pytest.raises(TypeError):
        OSC.Environment("Env_name1", tod, weather, rc, "dummy")


def test_oscenum():
    enum1 = OSC.enumerations._OscEnum("classname", "testname")
    assert enum1.get_name() == "testname"
    enum2 = OSC.enumerations._OscEnum("classname", "testname", min_minor_version=3)
    with pytest.raises(OSC.OpenSCENARIOVersionError):
        enum2.get_name()
    enum3 = OSC.enumerations._OscEnum("classname", "testname", max_minor_version=0)
    with pytest.raises(OSC.OpenSCENARIOVersionError):
        enum3.get_name()


def test_distancesteadystate():
    tdss = OSC.TargetDistanceSteadyState(1)
    tdss2 = OSC.TargetDistanceSteadyState(1)
    tdss3 = OSC.TargetDistanceSteadyState(12)
    assert tdss == tdss2
    assert tdss != tdss3
    prettyprint(tdss)

    tdss4 = OSC.TargetDistanceSteadyState.parse(tdss.get_element())
    assert tdss4 == tdss

    assert (
        version_validation("TargetDistanceSteadyState", tdss, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("TargetDistanceSteadyState", tdss, 1)
        == ValidationResponse.OK
    )
    assert (
        version_validation("TargetDistanceSteadyState", tdss, 2)
        == ValidationResponse.OK
    )


def test_timesteadystate():
    ttss = OSC.TargetTimeSteadyState(1)
    ttss2 = OSC.TargetTimeSteadyState(1)
    ttss3 = OSC.TargetTimeSteadyState(12)
    assert ttss == ttss2
    assert ttss != ttss3
    prettyprint(ttss)

    ttss4 = OSC.TargetTimeSteadyState.parse(ttss.get_element())
    assert ttss4 == ttss
    assert (
        version_validation("TargetTimeSteadyState", ttss, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert version_validation("TargetTimeSteadyState", ttss, 1) == ValidationResponse.OK
    assert version_validation("TargetTimeSteadyState", ttss, 2) == ValidationResponse.OK


def test_wind():
    w = OSC.Wind(0, 1)
    w2 = OSC.Wind(0, 1)
    w3 = OSC.Wind(1, 1)
    assert w == w2
    assert w != w3
    prettyprint(w)

    w4 = OSC.Wind.parse(w.get_element())
    assert w == w4

    assert version_validation("Wind", w, 0) == ValidationResponse.OSC_VERSION
    assert version_validation("Wind", w, 1) == ValidationResponse.OK
    assert version_validation("Wind", w, 2) == ValidationResponse.OK


def test_precipitation():
    p = OSC.Precipitation(OSC.PrecipitationType.rain, 1)
    p2 = OSC.Precipitation(OSC.PrecipitationType.rain, 1)
    p3 = OSC.Precipitation(OSC.PrecipitationType.rain, 2)
    assert p == p2
    assert p != p3
    prettyprint(p)

    p4 = OSC.Precipitation.parse(p.get_element())
    assert p4 == p

    assert version_validation("Precipitation", p, 0) == ValidationResponse.OK
    assert version_validation("Precipitation", p, 1) == ValidationResponse.OK
    assert version_validation("Precipitation", p, 2) == ValidationResponse.OK

    with pytest.raises(ValueError):
        OSC.Precipitation("dummy", 1)


def test_sun():
    s = OSC.Sun(1, 1, 1)
    s2 = OSC.Sun(1, 1, 1)
    s3 = OSC.Sun(1, 2, 1)

    assert s == s2
    assert s != s3
    prettyprint(s)

    s4 = OSC.Sun.parse(s.get_element())
    assert s == s4
    assert version_validation("Sun", s, 0) == ValidationResponse.OK
    assert version_validation("Sun", s, 1) == ValidationResponse.OK
    assert version_validation("Sun", s, 2) == ValidationResponse.OK


def test_fog():
    f = OSC.Fog(1, OSC.BoundingBox(1, 1, 1, 1, 1, 1))
    f2 = OSC.Fog(1, OSC.BoundingBox(1, 1, 1, 1, 1, 1))
    f3 = OSC.Fog(2)

    assert f == f2
    assert f != f3
    prettyprint(f)

    f4 = OSC.Fog.parse(f.get_element())
    assert f == f4
    assert version_validation("Fog", f, 0) == ValidationResponse.OK
    assert version_validation("Fog", f, 1) == ValidationResponse.OK
    assert version_validation("Fog", f, 2) == ValidationResponse.OK
    with pytest.raises(TypeError):
        OSC.Fog(1, "dummy")


def test_dynamicsConstraints():
    dc = OSC.DynamicsConstraints(2, 2, 3, 1, 2)
    dc2 = OSC.DynamicsConstraints(2, 2, 3, 1, 2)
    dc3 = OSC.DynamicsConstraints(3, 2, 2)
    prettyprint(dc.get_element())
    assert dc == dc2
    assert dc != dc3

    dc4 = OSC.DynamicsConstraints.parse(dc.get_element())
    prettyprint(dc4.get_element())
    assert dc == dc4
    assert (
        version_validation("DynamicConstraints", dc, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("DynamicConstraints", dc, 1)
        == ValidationResponse.OSC_VERSION
    )
    assert version_validation("DynamicConstraints", dc, 2) == ValidationResponse.OK

    assert version_validation("DynamicConstraints", dc3, 0) == ValidationResponse.OK
    assert version_validation("DynamicConstraints", dc3, 1) == ValidationResponse.OK
    assert version_validation("DynamicConstraints", dc3, 2) == ValidationResponse.OK


def test_license():
    l = OSC.License("MPL-2")
    l2 = OSC.License("MPL-2")
    l3 = OSC.License("MIT")
    assert l == l2
    assert l != l3
    prettyprint(l.get_element())

    l4 = OSC.License.parse(l.get_element())
    assert l4 == l
    assert version_validation("License", l, 0) == ValidationResponse.OSC_VERSION
    assert version_validation("License", l, 1) == ValidationResponse.OK
    assert version_validation("License", l, 2) == ValidationResponse.OK


def test_absoluteSpeed():
    inst = OSC.AbsoluteSpeed(1)
    inst2 = OSC.AbsoluteSpeed(1)
    inst3 = OSC.AbsoluteSpeed(4)
    assert inst == inst2
    assert inst != inst3
    inst4 = OSC.AbsoluteSpeed(1, steadyState=OSC.TargetTimeSteadyState(2))
    prettyprint(inst4)
    inst5 = OSC.AbsoluteSpeed(1, steadyState=OSC.TargetTimeSteadyState(2))
    inst6 = OSC.AbsoluteSpeed(1, steadyState=OSC.TargetDistanceSteadyState(2))
    assert inst4 == inst5
    assert inst4 != inst6

    inst7 = OSC.AbsoluteSpeed.parse(inst4.get_element())
    prettyprint(inst7.get_element())
    assert inst4 == inst7

    assert version_validation("FinalSpeed", inst, 0) == ValidationResponse.OK
    assert version_validation("FinalSpeed", inst, 1) == ValidationResponse.OK
    assert version_validation("FinalSpeed", inst, 2) == ValidationResponse.OK

    assert version_validation("FinalSpeed", inst4, 0) == ValidationResponse.OSC_VERSION
    assert version_validation("FinalSpeed", inst4, 1) == ValidationResponse.OK
    assert version_validation("FinalSpeed", inst4, 2) == ValidationResponse.OK

    with pytest.raises(TypeError):
        OSC.AbsoluteSpeed(1, "dummy")


def test_relativeSpeedToMaster():
    inst = OSC.RelativeSpeedToMaster(1, OSC.SpeedTargetValueType.delta)
    inst2 = OSC.RelativeSpeedToMaster(1, OSC.SpeedTargetValueType.delta)
    inst3 = OSC.RelativeSpeedToMaster(2, OSC.SpeedTargetValueType.delta)
    assert inst == inst2
    assert inst != inst3
    inst4 = OSC.RelativeSpeedToMaster(
        1, OSC.SpeedTargetValueType.delta, steadyState=OSC.TargetTimeSteadyState(2)
    )
    prettyprint(inst4)
    inst5 = OSC.RelativeSpeedToMaster(
        1, OSC.SpeedTargetValueType.delta, steadyState=OSC.TargetDistanceSteadyState(1)
    )

    inst6 = OSC.RelativeSpeedToMaster.parse(inst4.get_element())
    assert inst6 == inst4

    assert version_validation("FinalSpeed", inst, 0) == ValidationResponse.OK
    assert version_validation("FinalSpeed", inst, 1) == ValidationResponse.OK
    assert version_validation("FinalSpeed", inst, 2) == ValidationResponse.OK

    assert version_validation("FinalSpeed", inst4, 0) == ValidationResponse.OSC_VERSION
    assert version_validation("FinalSpeed", inst4, 1) == ValidationResponse.OK
    assert version_validation("FinalSpeed", inst4, 2) == ValidationResponse.OK

    with pytest.raises(ValueError):
        OSC.RelativeSpeedToMaster(1, "dummy", steadyState=OSC.TargetTimeSteadyState(2))
    with pytest.raises(TypeError):
        OSC.RelativeSpeedToMaster(
            1, OSC.SpeedTargetValueType.delta, steadyState="dummy"
        )


def test_targetDistanceSteadyState():
    inst = OSC.TargetDistanceSteadyState(1)
    inst2 = OSC.TargetDistanceSteadyState(1)
    inst3 = OSC.TargetDistanceSteadyState(2)
    assert inst == inst2
    assert inst != inst3
    prettyprint(inst)

    assert (
        version_validation("TargetDistanceSteadyState", inst, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("TargetDistanceSteadyState", inst, 1)
        == ValidationResponse.OK
    )
    assert (
        version_validation("TargetDistanceSteadyState", inst, 2)
        == ValidationResponse.OK
    )


def test_targetTimeSteadyState():
    inst = OSC.TargetTimeSteadyState(1)
    inst2 = OSC.TargetTimeSteadyState(1)
    inst3 = OSC.TargetTimeSteadyState(2)
    assert inst == inst2
    assert inst != inst3
    prettyprint(inst)
    assert (
        version_validation("TargetTimeSteadyState", inst, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert version_validation("TargetTimeSteadyState", inst, 1) == ValidationResponse.OK
    assert version_validation("TargetTimeSteadyState", inst, 2) == ValidationResponse.OK


def test_value_constraint_group():
    vc = OSC.ValueConstraint(OSC.Rule.equalTo, "equalTo")
    vc2 = OSC.ValueConstraint(OSC.Rule.notEqualTo, "equalTo")
    vc3 = OSC.ValueConstraint(OSC.Rule.equalTo, "notEqualTo")
    vcg = OSC.ValueConstraintGroup()
    vcg2 = OSC.ValueConstraintGroup()
    vcg3 = OSC.ValueConstraintGroup()
    vcg.add_value_constraint(vc)
    vcg.add_value_constraint(vc2)
    vcg2.add_value_constraint(vc)
    vcg2.add_value_constraint(vc2)
    vcg3.add_value_constraint(vc)
    vcg3.add_value_constraint(vc3)
    prettyprint(vcg.get_element())
    assert vcg == vcg2
    assert vcg != vcg3
    vcg4 = OSC.ValueConstraintGroup.parse(vcg.get_element())
    assert vcg == vcg4
    assert (
        version_validation("ValueConstraintGroup", vcg, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert version_validation("ValueConstraintGroup", vcg, 1) == ValidationResponse.OK
    assert version_validation("ValueConstraintGroup", vcg, 2) == ValidationResponse.OK

    with pytest.raises(TypeError):
        vcg.add_value_constraint("dummy")


def test_value_constraint():
    vc = OSC.ValueConstraint(OSC.Rule.equalTo, "equalTo")
    vc2 = OSC.ValueConstraint(OSC.Rule.equalTo, "equalTo")
    vc3 = OSC.ValueConstraint(OSC.Rule.notEqualTo, "equalTo")
    prettyprint(vc.get_element())
    assert vc == vc2
    assert vc != vc3
    vc4 = OSC.ValueConstraint.parse(vc.get_element())
    assert vc == vc4
    assert (
        version_validation("ValueConstraint", vc, 0) == ValidationResponse.OSC_VERSION
    )
    assert version_validation("ValueConstraint", vc, 1) == ValidationResponse.OK
    assert version_validation("ValueConstraint", vc, 2) == ValidationResponse.OK
    with pytest.raises(ValueError):
        OSC.ValueConstraint("dummy", 3)


def test_convert_float():
    assert OSC.convert_float(1) == 1.0
    assert OSC.convert_float("1.1") == 1.1
    assert OSC.convert_float("$asdf") == "$asdf"
    with pytest.raises(ValueError):
        OSC.convert_float("asdf")


def test_convert_int():
    assert OSC.convert_int(1) == 1
    assert OSC.convert_int("1") == 1
    assert OSC.convert_int("$asdf") == "$asdf"
    with pytest.raises(ValueError):
        OSC.convert_int("asdf")


def test_convert_bool():
    assert OSC.convert_bool(1) == True

    assert OSC.convert_bool(False) == False
    assert OSC.convert_bool("$asdf") == "$asdf"
    assert OSC.convert_bool("0") == False
    assert OSC.convert_bool("1") == True

    with pytest.raises(ValueError):
        OSC.convert_bool("asdf")


def test_colorrgb():
    c = OSC.ColorRGB(1, 2, 3)
    c2 = OSC.ColorRGB(1, 2, 3)
    c3 = OSC.ColorRGB(1, 2, 4)
    prettyprint(c)
    assert c == c2
    assert c != c3
    c4 = OSC.ColorRGB.parse(c.get_element())
    assert c == c4


def test_colorcmyk():
    c = OSC.ColorCMYK(1, 2, 3, 1)
    c2 = OSC.ColorCMYK(1, 2, 3, 1)
    c3 = OSC.ColorCMYK(1, 2, 4, 2)
    prettyprint(c)
    assert c == c2
    assert c != c3
    c4 = OSC.ColorCMYK.parse(c.get_element())
    assert c == c4


def test_color():
    c = OSC.Color(OSC.ColorType.black, OSC.ColorCMYK(1, 2, 3, 1))

    c2 = OSC.Color(OSC.ColorType.black, OSC.ColorCMYK(1, 2, 3, 1))
    c3 = OSC.Color(OSC.ColorType.black, OSC.ColorRGB(1, 2, 3))
    prettyprint(c)
    assert c == c2
    assert c != c3
    c4 = OSC.Color.parse(c.get_element())
    assert c == c4
    assert version_validation("Color", c, 0) == ValidationResponse.OSC_VERSION
    assert version_validation("Color", c, 1) == ValidationResponse.OSC_VERSION
    assert version_validation("Color", c, 2) == ValidationResponse.OK

    with pytest.raises(ValueError):
        OSC.Color("dummy", OSC.ColorCMYK(1, 2, 3, 1))
    with pytest.raises(TypeError):
        OSC.Color(OSC.ColorType.black, "dummy")


def test_userdefinedlight():
    udl = OSC.UserDefinedLight("superlight")
    udl2 = OSC.UserDefinedLight("superlight")
    udl3 = OSC.UserDefinedLight("less super light")
    prettyprint(udl)
    assert udl == udl2
    assert udl != udl3
    udl4 = OSC.UserDefinedLight.parse(udl.get_element())
    assert udl4 == udl
    assert (
        version_validation("UserDefinedLight", udl, 0) == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("UserDefinedLight", udl, 1) == ValidationResponse.OSC_VERSION
    )
    assert version_validation("UserDefinedLight", udl, 2) == ValidationResponse.OK


def test_lightstate():
    ls = OSC.utils._LightState(
        OSC.LightMode.on,
        color=OSC.Color(OSC.ColorType.black, OSC.ColorRGB(0, 0, 0)),
        intensity=200,
        flashing_off_duration=0.3,
        flashing_on_duration=0.2,
    )
    ls2 = OSC.utils._LightState(
        OSC.LightMode.on,
        color=OSC.Color(OSC.ColorType.black, OSC.ColorRGB(0, 0, 0)),
        intensity=200,
        flashing_off_duration=0.3,
        flashing_on_duration=0.2,
    )
    ls3 = OSC.utils._LightState(OSC.LightMode.flashing)
    prettyprint(ls)
    print(ls3)
    prettyprint(ls3)
    assert ls == ls2
    assert ls != ls3
    ls4 = OSC.utils._LightState.parse(ls.get_element())
    assert ls == ls4

    assert version_validation("LightState", ls, 0) == ValidationResponse.OSC_VERSION
    assert version_validation("LightState", ls, 1) == ValidationResponse.OSC_VERSION
    assert version_validation("LightState", ls, 2) == ValidationResponse.OK

    with pytest.raises(ValueError):
        OSC.utils._LightState(
            "dummy",
            color=OSC.Color(OSC.ColorType.black, OSC.ColorRGB(0, 0, 0)),
            intensity=200,
            flashing_off_duration=0.3,
            flashing_on_duration=0.2,
        )
    with pytest.raises(TypeError):
        OSC.utils._LightState(
            OSC.LightMode.on,
            color="dummy",
            intensity=200,
            flashing_off_duration=0.3,
            flashing_on_duration=0.2,
        )


def test_animationfile():
    ani = OSC.AnimationFile("file_ref")
    ani2 = OSC.AnimationFile("file_ref", 1.5)
    prettyprint(ani2.get_element())
    ani3 = OSC.AnimationFile("file_ref2", 1.5)
    assert ani != ani2
    assert ani2 != ani3

    ani4 = OSC.AnimationFile.parse(ani2.get_element())
    prettyprint(ani4.get_element())
    assert ani4 == ani2

    assert version_validation("AnimationFile", ani, 0) == ValidationResponse.OSC_VERSION
    assert version_validation("AnimationFile", ani, 1) == ValidationResponse.OSC_VERSION
    assert version_validation("AnimationFile", ani, 2) == ValidationResponse.OK


def test_directionoftraveldistribution():
    dotd = OSC.DirectionOfTravelDistribution(1, 2)
    dotd2 = OSC.DirectionOfTravelDistribution(1, 2)
    prettyprint(dotd.get_element())
    dotd3 = OSC.DirectionOfTravelDistribution(1, 1)
    assert dotd == dotd2
    assert dotd != dotd3

    dotd4 = OSC.DirectionOfTravelDistribution.parse(dotd.get_element())
    prettyprint(dotd4.get_element())
    assert dotd4 == dotd
    assert (
        version_validation("DirectionOfTravelDistribution", dotd, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("DirectionOfTravelDistribution", dotd, 1)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("DirectionOfTravelDistribution", dotd, 2)
        == ValidationResponse.OK
    )


def test_userdefinedanimation():
    ani = OSC.UserDefinedAnimation("animation_type")
    ani2 = OSC.UserDefinedAnimation("animation_type2")
    ani3 = OSC.UserDefinedAnimation("animation_type")
    prettyprint(ani.get_element())
    assert ani != ani2
    assert ani == ani3
    ani4 = OSC.UserDefinedAnimation.parse(ani.get_element())
    assert ani == ani4
    assert (
        version_validation("UserDefinedAnimation", ani, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("UserDefinedAnimation", ani, 1)
        == ValidationResponse.OSC_VERSION
    )
    assert version_validation("UserDefinedAnimation", ani, 2) == ValidationResponse.OK


def test_userdefinedcomponent():
    ani = OSC.UserDefinedComponent("component_type")
    ani2 = OSC.UserDefinedComponent("component_type2")
    ani3 = OSC.UserDefinedComponent("component_type")
    prettyprint(ani.get_element())
    assert ani != ani2
    assert ani == ani3
    ani4 = OSC.UserDefinedComponent.parse(ani.get_element())
    assert ani == ani4
    assert (
        version_validation("UserDefinedComponent", ani, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("UserDefinedComponent", ani, 1)
        == ValidationResponse.OSC_VERSION
    )
    assert version_validation("UserDefinedComponent", ani, 2) == ValidationResponse.OK


def test_pedestriananimation():
    pa = OSC.PedestrianAnimation(OSC.PedestrianMotionType.running, "animation1")
    pa2 = OSC.PedestrianAnimation(OSC.PedestrianMotionType.running, "animation2")
    pa3 = OSC.PedestrianAnimation(OSC.PedestrianMotionType.ducking, "animation1")
    prettyprint(pa.get_element())
    assert pa != pa2
    assert pa != pa3
    pa4 = OSC.PedestrianAnimation(OSC.PedestrianMotionType.running, "animation1")
    pa.add_gesture(OSC.PedestrianGestureType.sandwichLeftHand)
    pa4.add_gesture(OSC.PedestrianGestureType.sandwichRightHand)
    assert pa != pa4
    pa.add_gesture(OSC.PedestrianGestureType.sandwichRightHand)
    prettyprint(pa.get_element())
    pa5 = OSC.PedestrianAnimation.parse(pa.get_element())
    assert pa5 == pa
    assert (
        version_validation("PedestrianAnimation", pa, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("PedestrianAnimation", pa, 1)
        == ValidationResponse.OSC_VERSION
    )
    assert version_validation("PedestrianAnimation", pa, 2) == ValidationResponse.OK
    assert version_validation("PedestrianAnimation", pa4, 2) == ValidationResponse.OK
    with pytest.raises(ValueError):
        OSC.PedestrianAnimation(
            "dummy",
        )


def test_vehiclecomponent():
    vc = OSC.utils._VehicleComponent(OSC.VehicleComponentType.doorFrontLeft)
    vc2 = OSC.utils._VehicleComponent(OSC.VehicleComponentType.doorRearLeft)
    prettyprint(vc.get_element())
    assert vc != vc2
    vc3 = OSC.utils._VehicleComponent(OSC.VehicleComponentType.doorFrontLeft)
    assert vc == vc3
    vc4 = OSC.utils._VehicleComponent.parse(vc.get_element())
    prettyprint(vc4.get_element())
    assert vc4 == vc
    assert (
        version_validation("VehicleComponent", vc, 0) == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("VehicleComponent", vc, 1) == ValidationResponse.OSC_VERSION
    )
    assert version_validation("VehicleComponent", vc, 2) == ValidationResponse.OK
    with pytest.raises(ValueError):
        OSC.utils._VehicleComponent("dummy")


def test_componentanimation():
    vc = OSC.utils._VehicleComponent(OSC.VehicleComponentType.doorFrontLeft)
    vc2 = OSC.utils._VehicleComponent(OSC.VehicleComponentType.doorRearRight)
    udc = OSC.UserDefinedComponent("my_component")
    udc2 = OSC.UserDefinedComponent("my_component2")
    udc3 = OSC.UserDefinedComponent("doorFrontLeft")
    ca = OSC.utils._ComponentAnimation(vc)
    prettyprint(ca.get_element())
    ca2 = OSC.utils._ComponentAnimation(vc2)
    assert ca != ca2
    ca3 = OSC.utils._ComponentAnimation(udc)
    prettyprint(ca3.get_element())
    ca4 = OSC.utils._ComponentAnimation(udc3)
    prettyprint(ca4.get_element())
    assert ca != ca3
    assert ca != ca4
    ca5 = OSC.utils._ComponentAnimation(udc2)
    assert ca3 != ca5

    ca6 = OSC.utils._ComponentAnimation.parse(ca.get_element())
    prettyprint(ca6.get_element())
    assert ca6 == ca
    ca7 = OSC.utils._ComponentAnimation.parse(ca2.get_element())
    assert ca7 == ca2
    ca8 = OSC.utils._ComponentAnimation.parse(ca4.get_element())
    assert ca8 == ca4
    assert ca8 != ca

    # assert version_validation("ComponentAnimation", ca, 2) == ValidationResponse.OK


@pytest.mark.parametrize(
    "input",
    [
        OSC.utils._ComponentAnimation(
            OSC.utils._VehicleComponent(OSC.VehicleComponentType.doorFrontLeft)
        ),
        OSC.PedestrianAnimation(OSC.PedestrianMotionType.bendingDown),
        OSC.AnimationFile("my_animation"),
        OSC.UserDefinedAnimation("Myparam"),
    ],
)
def test_global_action_factory(input):
    test_element = ET.Element("AnimationType")
    test_element.append(input.get_element())
    factoryoutput = OSC.utils._AnimationTypeFactory.parse_animationtype(test_element)
    prettyprint(input, None)
    prettyprint(factoryoutput, None)
    assert input == factoryoutput


def test_version_base():
    version = OSC.VersionBase()
    version.setVersion(minor=2)
    assert version.isVersion(minor=2)
    assert not version.isVersion(minor=1)
    assert version.isVersionEqLarger(minor=1)
    assert version.isVersionEqLarger(minor=2)
    assert version.isVersionEqLess(minor=2)
    assert not version.isVersionEqLess(minor=1)

    version.setVersion(minor=1)
    assert version.isVersion(minor=1)
    assert not version.isVersion(minor=2)
    assert not version.isVersionEqLarger(minor=2)
    assert version.isVersionEqLarger(minor=0)
    assert version.isVersionEqLess(minor=2)
    assert not version.isVersionEqLess(minor=0)


def test_convert_enum():
    e1 = OSC.DynamicsDimension.time
    e2 = "$param"
    assert OSC.convert_enum(e1, OSC.DynamicsDimension).get_name() == "time"
    assert OSC.convert_enum("time", OSC.DynamicsDimension).get_name() == "time"
    assert OSC.convert_enum("$param", OSC.DynamicsDimension).get_name() == "$param"
    with pytest.raises(TypeError):
        OSC.convert_enum(1, OSC.DynamicsDimension)
    with pytest.raises(TypeError):
        OSC.convert_enum(OSC.DynamicsShapes.cubic, OSC.DynamicsDimension)
    with pytest.raises(ValueError):
        OSC.convert_enum("hello", OSC.DynamicsDimension)
    assert OSC.convert_enum(None, OSC.DynamicsDimension, True) == None
    with pytest.raises(TypeError):
        OSC.convert_enum(None, OSC.DynamicsDimension, False) == None
