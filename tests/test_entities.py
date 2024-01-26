"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2022 The scenariogeneration Authors.

"""

import pytest

from scenariogeneration import xosc as OSC
from scenariogeneration import prettyprint
from scenariogeneration.xosc.utils import CatalogReference, EntityRef
from .xml_validator import version_validation, ValidationResponse
import os


@pytest.fixture(autouse=True)
def reset_version():
    OSC.enumerations.VersionBase().setVersion(minor=2)


def test_properties():
    prop = OSC.Properties()
    prop.add_file("myprops.xml")
    prettyprint(prop.get_element())
    prop.add_property("mything", "2")
    prettyprint(prop.get_element())
    prop.add_property("theotherthing", "true")

    prop2 = OSC.Properties()
    prop2.add_file("myprops.xml")
    prop2.add_property("mything", "2")
    prop2.add_property("theotherthing", "true")

    prop3 = OSC.Properties()
    prop3.add_file("myprops.xml")

    assert prop == prop2
    assert prop != prop3

    assert version_validation("Properties", prop2, 0) == ValidationResponse.OK
    assert version_validation("Properties", prop2, 1) == ValidationResponse.OK
    assert version_validation("Properties", prop2, 2) == ValidationResponse.OK


def test_axle():
    ba = OSC.Axle(1, 1, 2, 1, 1)
    prettyprint(ba.get_element())
    ba2 = OSC.Axle(1, 1, 2, 1, 1)
    ba3 = OSC.Axle(1, 1, 2, 1, 12)
    assert ba == ba2
    assert ba != ba3
    ba4 = OSC.Axle.parse(ba.get_element())
    assert ba == ba4
    assert version_validation("Axle", ba2, 0) == ValidationResponse.OK
    assert version_validation("Axle", ba, 1) == ValidationResponse.OK
    assert version_validation("Axle", ba, 2) == ValidationResponse.OK


def test_axles():
    fa = OSC.Axle(2, 2, 2, 1, 1)
    ra = OSC.Axle(1, 1, 2, 1, 1)
    aa = OSC.Axle(1, 1, 2, 1, 1)
    aa2 = OSC.Axle(2, 3, 1, 3, 2)
    axles = OSC.Axles(fa, ra)
    axles.add_axle(aa)
    axles.add_axle(aa2)
    prettyprint(axles.get_element())
    axles2 = OSC.Axles(fa, ra)
    axles2.add_axle(aa)
    axles2.add_axle(aa2)
    axles3 = OSC.Axles(fa, ra)
    assert axles == axles2
    assert axles != axles3
    axles4 = OSC.Axles.parse(axles.get_element())
    assert axles == axles4
    assert version_validation("Axles", axles, 0) == ValidationResponse.OK
    assert version_validation("Axles", axles, 1) == ValidationResponse.OK
    assert version_validation("Axles", axles, 2) == ValidationResponse.OK
    with pytest.raises(TypeError):
        OSC.Axles("dummy", ra)
    with pytest.raises(TypeError):
        OSC.Axles(fa, "dummy")
    with pytest.raises(TypeError):
        axles.add_axle("dummy")


def test_vehicle(tmpdir):
    bb = OSC.BoundingBox(2, 5, 1.5, 1.5, 0, 0.2)
    fa = OSC.Axle(2, 2, 2, 1, 1)
    ba = OSC.Axle(1, 1, 2, 1, 1)

    veh = OSC.Vehicle("mycar", OSC.VehicleCategory.car, bb, fa, ba, 150, 10, 10)

    prettyprint(veh.get_element())
    veh.add_property_file("propfile.xml")
    veh.add_property("myprop", "12")
    veh.add_axle(ba)
    param = OSC.Parameter("mypar", OSC.ParameterType.integer, "1")
    veh.add_parameter(param)

    prettyprint(veh.get_element())

    veh2 = OSC.Vehicle("mycar", OSC.VehicleCategory.car, bb, fa, ba, 150, 10, 10)
    veh2.add_property_file("propfile.xml")
    veh2.add_property("myprop", "12")
    veh2.add_axle(ba)
    veh2.add_parameter(param)

    veh3 = OSC.Vehicle(
        "mycar",
        OSC.VehicleCategory.car,
        bb,
        fa,
        ba,
        150,
        10,
        10,
        2000,
        "model",
        1,
        1,
        OSC.Role.police,
    )
    prettyprint(veh3)
    assert veh == veh2
    assert veh != veh3

    veh4 = OSC.Vehicle.parse(veh.get_element())
    assert veh4 == veh
    prettyprint(veh4.get_element())
    veh5 = OSC.Vehicle.parse(veh3.get_element())
    prettyprint(veh5)
    assert veh5 == veh3

    assert version_validation("Vehicle", veh, 0) == ValidationResponse.OK
    assert version_validation("Vehicle", veh, 1) == ValidationResponse.OK
    assert version_validation("Vehicle", veh, 2) == ValidationResponse.OK

    assert version_validation("Vehicle", veh3, 0) == ValidationResponse.OSC_VERSION
    assert version_validation("Vehicle", veh3, 1) == ValidationResponse.OSC_VERSION
    assert version_validation("Vehicle", veh3, 2) == ValidationResponse.OK

    veh6 = OSC.Vehicle(
        "mycar",
        OSC.VehicleCategory.car,
        bb,
        fa,
        ba,
        150,
        10,
        10,
        2000,
        "model",
    )

    assert version_validation("Vehicle", veh6, 0) == ValidationResponse.OSC_VERSION
    assert version_validation("Vehicle", veh6, 1) == ValidationResponse.OK
    assert version_validation("Vehicle", veh6, 2) == ValidationResponse.OK

    veh.dump_to_catalog(
        os.path.join(tmpdir, "my_catalog.xosc"),
        "VehicleCatalog",
        "test catalog",
        "Mandolin",
    )

    with pytest.raises(ValueError):
        OSC.Vehicle("car", "dummy", bb, fa, ba, 150, 10, 10)
    with pytest.raises(TypeError):
        OSC.Vehicle("car", OSC.VehicleCategory.bicycle, "dummy", fa, ba, 150, 10, 10)
    with pytest.raises(TypeError):
        OSC.Vehicle("car", OSC.VehicleCategory.bicycle, bb, "dummy", ba, 150, 10, 10)
    with pytest.raises(TypeError):
        OSC.Vehicle("car", OSC.VehicleCategory.bicycle, bb, fa, "dummy", 150, 10, 10)
    with pytest.raises(ValueError):
        OSC.Vehicle(
            "car", OSC.VehicleCategory.bicycle, bb, fa, ba, 150, 10, 10, role="dummy"
        )
    with pytest.raises(TypeError):
        veh.add_parameter("dummy")
    with pytest.raises(TypeError):
        veh.add_axle("dummy")


def test_pedestrian(tmpdir):
    bb = OSC.BoundingBox(2, 5, 1.5, 1.5, 0, 0.2)
    ped = OSC.Pedestrian(
        "myped", 100, OSC.PedestrianCategory.pedestrian, bb, "ped", OSC.Role.police
    )

    prettyprint(ped.get_element())
    ped.add_property_file("propfile.xml")
    ped.add_property("myprop", "12")
    param = OSC.Parameter("mypar", OSC.ParameterType.integer, "1")
    ped.add_parameter(param)

    prettyprint(ped.get_element())

    ped2 = OSC.Pedestrian(
        "myped", 100, OSC.PedestrianCategory.pedestrian, bb, "ped", OSC.Role.police
    )
    ped2.add_property_file("propfile.xml")
    ped2.add_property("myprop", "12")
    ped2.add_parameter(param)
    ped3 = OSC.Pedestrian(
        "myped", 100, OSC.PedestrianCategory.pedestrian, bb, "test_model"
    )

    assert ped == ped2
    assert ped != ped3

    ped4 = OSC.Pedestrian.parse(ped.get_element())
    assert ped4 == ped
    ped.dump_to_catalog(
        os.path.join(tmpdir, "my_catalog.xosc"),
        "PedestrianCatalog",
        "test catalog",
        "Mandolin",
    )
    assert version_validation("Pedestrian", ped, 0) == ValidationResponse.OSC_VERSION
    assert version_validation("Pedestrian", ped, 1) == ValidationResponse.OSC_VERSION
    assert version_validation("Pedestrian", ped, 2) == ValidationResponse.OK

    assert version_validation("Pedestrian", ped3, 0) == ValidationResponse.OK
    assert version_validation("Pedestrian", ped3, 1) == ValidationResponse.OK
    assert version_validation("Pedestrian", ped3, 2) == ValidationResponse.OK

    with pytest.raises(ValueError):
        OSC.Pedestrian("myped", 100, "dummy", bb, "ped", OSC.Role.police)
    with pytest.raises(TypeError):
        OSC.Pedestrian(
            "myped",
            100,
            OSC.PedestrianCategory.pedestrian,
            "dummy",
            "ped",
            OSC.Role.police,
        )
    with pytest.raises(ValueError):
        OSC.Pedestrian(
            "myped", 100, OSC.PedestrianCategory.pedestrian, bb, "ped", "dummy"
        )
    with pytest.raises(TypeError):
        ped.add_parameter("dummy")


def test_miscobj(tmpdir):
    bb = OSC.BoundingBox(2, 5, 1.5, 1.5, 0, 0.2)
    veh = OSC.MiscObject("mycar", 100, OSC.MiscObjectCategory.obstacle, bb)

    prettyprint(veh.get_element())
    veh.add_property_file("propfile.xml")
    veh.add_property_file("propfile2.xml")
    veh.add_property("myprop", "12")
    param = OSC.Parameter("mypar", OSC.ParameterType.integer, "1")
    param2 = OSC.Parameter("myparam1", OSC.ParameterType.double, "0.01")
    veh.add_parameter(param)
    veh.add_parameter(param2)
    prettyprint(veh.get_element())

    veh2 = OSC.MiscObject("mycar", 100, OSC.MiscObjectCategory.obstacle, bb)
    veh2.add_property_file("propfile.xml")
    veh2.add_property_file("propfile2.xml")
    veh2.add_property("myprop", "12")
    veh2.add_parameter(param)
    veh2.add_parameter(param2)

    veh3 = OSC.MiscObject("mycar", 100, OSC.MiscObjectCategory.obstacle, bb)
    veh4 = OSC.MiscObject.parse(veh3.get_element())
    assert veh3 == veh4
    assert veh == veh2
    assert veh != veh3
    veh5 = OSC.MiscObject.parse(veh.get_element())
    prettyprint(veh5.get_element())
    assert veh5 == veh
    veh.dump_to_catalog(
        os.path.join(tmpdir, "my_catalog.xosc"),
        "MiscObjectCatalog",
        "test catalog",
        "Mandolin",
    )
    assert version_validation("MiscObject", veh, 0) == ValidationResponse.OK
    assert version_validation("MiscObject", veh, 1) == ValidationResponse.OK
    assert version_validation("MiscObject", veh, 2) == ValidationResponse.OK
    with pytest.raises(ValueError):
        OSC.MiscObject("mycar", 100, "dummy", bb)
    with pytest.raises(TypeError):
        OSC.MiscObject("mycar", 100, OSC.MiscObjectCategory.obstacle, "dummy")


def test_entity():
    object_type_list = [OSC.ObjectType.vehicle, OSC.ObjectType.pedestrian]
    ent = OSC.Entity("ego", object_type=object_type_list)
    prettyprint(ent.get_element())
    ent3 = OSC.Entity("ego", entityref=["Ego", "Ego2", "Ego3"])
    prettyprint(ent3.get_element())
    ent2 = OSC.Entity("ego", object_type=OSC.ObjectType.vehicle)
    ent4 = OSC.Entity("ego", object_type=object_type_list)
    assert ent != ent2
    assert ent == ent4

    ent5 = OSC.Entity.parse(ent.get_element())
    assert ent5 == ent

    ent6 = OSC.Entity.parse(ent3.get_element())
    prettyprint(ent6.get_element())
    assert ent6 == ent3

    assert version_validation("EntitySelection", ent, 0) == ValidationResponse.OK
    assert version_validation("EntitySelection", ent, 1) == ValidationResponse.OK
    assert version_validation("EntitySelection", ent, 2) == ValidationResponse.OK

    with pytest.raises(ValueError):
        OSC.Entity("ego", object_type="dummy")
    with pytest.raises(ValueError):
        OSC.Entity("ego", object_type=["dummy", OSC.ObjectType.pedestrian])


def test_scenarioobject():
    prop = OSC.Properties()
    prop.add_property("mything", "2")
    prop.add_property("theotherthing", "true")
    cnt = OSC.Controller("mycontroller", prop)

    bb = OSC.BoundingBox(2, 5, 1.5, 1.5, 0, 0.2)
    fa = OSC.Axle(2, 2, 2, 1, 1)
    ba = OSC.Axle(1, 1, 2, 1, 1)
    veh = OSC.Vehicle("mycar", OSC.VehicleCategory.car, bb, fa, ba, 150, 10, 10)
    veh.add_property_file("propfile.xml")
    veh.add_property("myprop", "12")
    veh.add_axle(ba)
    param = OSC.Parameter("mypar", OSC.ParameterType.integer, "1")
    veh.add_parameter(param)
    cnt2 = [
        OSC.Controller("mycontroller", prop),
        OSC.Controller("mycontroller_2", prop),
    ]
    so = OSC.ScenarioObject("name", veh, cnt)
    so2 = OSC.ScenarioObject("name", veh, cnt)
    so3 = OSC.ScenarioObject("name", veh, cnt2)
    prettyprint(so.get_element())
    assert so == so2
    assert so != so3
    prettyprint(so3.get_element())
    so4 = OSC.ScenarioObject.parse(so.get_element())

    assert so4 == so
    so5 = OSC.ScenarioObject.parse(so3.get_element())
    assert so5 == so3
    assert version_validation("ScenarioObject", so, 0) == ValidationResponse.OK
    assert version_validation("ScenarioObject", so, 1) == ValidationResponse.OK
    assert version_validation("ScenarioObject", so, 2) == ValidationResponse.OK

    with pytest.raises(TypeError):
        OSC.ScenarioObject("my car", "dummy")
    with pytest.raises(TypeError):
        OSC.ScenarioObject("my car", veh, "dummy")


def test_entities():
    bb = OSC.BoundingBox(2, 5, 1.5, 1.5, 0, 0.2)
    fa = OSC.Axle(2, 2, 2, 1, 1)
    ba = OSC.Axle(1, 1, 2, 1, 1)
    veh = OSC.Vehicle("mycar", OSC.VehicleCategory.car, bb, fa, ba, 150, 10, 10)
    param = OSC.Parameter("mypar", OSC.ParameterType.integer, "1")
    veh.add_parameter(param)

    entities = OSC.Entities()
    entities.add_scenario_object("Ego", veh)
    entities.add_scenario_object("Target_1", veh)
    entities.add_entity_bytype("Target_2", OSC.ObjectType.vehicle)
    entities.add_entity_byref("Target_3", "something")
    prettyprint(entities.get_element())

    entities2 = OSC.Entities()
    entities2.add_scenario_object("Ego", veh)
    entities2.add_scenario_object("Target_1", veh)
    entities2.add_entity_bytype("Target_2", OSC.ObjectType.vehicle)
    entities2.add_entity_byref("Target_3", "something")

    entities3 = OSC.Entities()
    entities3.add_scenario_object("Ego", veh)
    entities3.add_scenario_object("Target_1", veh)
    entities3.add_entity_bytype("Target_2", OSC.ObjectType.vehicle)

    assert entities == entities2
    assert entities != entities3

    entities4 = OSC.Entities.parse(entities2.get_element())
    prettyprint(entities4.get_element())
    assert entities == entities4

    assert version_validation("Entities", entities, 0) == ValidationResponse.OK
    assert version_validation("Entities", entities, 1) == ValidationResponse.OK
    assert version_validation("Entities", entities, 2) == ValidationResponse.OK

    with pytest.raises(TypeError):
        entities.add_scenario_object("asdf", "dummy")
    with pytest.raises(TypeError):
        entities.add_scenario_object("asdf", veh, "dummy")
    with pytest.raises(ValueError):
        entities.add_entity_bytype("qwer", "dummy")


def test_controller(tmpdir):
    prop = OSC.Properties()
    prop.add_property("mything", "2")
    prop.add_property("theotherthing", "true")

    cnt = OSC.Controller("mycontroler", prop)
    prettyprint(cnt.get_element())
    cnt2 = OSC.Controller("mycontroler", prop)
    cnt3 = OSC.Controller("mycontroler2", prop)
    assert cnt == cnt2
    assert cnt != cnt3

    assert version_validation("Controller", cnt, 0) == ValidationResponse.OK
    assert version_validation("Controller", cnt, 1) == ValidationResponse.OK
    assert version_validation("Controller", cnt, 2) == ValidationResponse.OK

    cnt.dump_to_catalog(
        os.path.join(tmpdir, "my_catalog.xosc"),
        "ControllerCatalog",
        "test catalog",
        "Mandolin",
    )

    with pytest.raises(TypeError):
        OSC.Controller("my cnt", "dummy")
    with pytest.raises(TypeError):
        cnt.add_parameter("dummy")


def test_controller_in_Entities():
    bb = OSC.BoundingBox(2, 5, 1.5, 1.5, 0, 0.2)
    fa = OSC.Axle(2, 2, 2, 1, 1)
    ba = OSC.Axle(1, 1, 2, 1, 1)
    veh = OSC.Vehicle("mycar", OSC.VehicleCategory.car, bb, fa, ba, 150, 10, 10)

    prop = OSC.Properties()
    prop.add_property("mything", "2")
    prop.add_property("theotherthing", "true")

    cnt = OSC.Controller("mycontroler", prop)
    cnt2 = OSC.Controller("mycontroler", prop)

    entities = OSC.Entities()
    entities.add_scenario_object("Target_1", veh, cnt)

    prettyprint(entities.get_element())

    entities2 = OSC.Entities()
    entities2.add_scenario_object("Target_1", veh, cnt)

    entities3 = OSC.Entities()
    entities3.add_scenario_object("Target_2", veh, cnt)
    assert entities == entities2
    assert entities != entities3

    entities_multi_cnt = OSC.Entities()
    entities_multi_cnt.add_scenario_object("Target_2", veh, [cnt, cnt2])
    prettyprint(entities_multi_cnt.get_element())
    assert entities3 != entities_multi_cnt

    assert version_validation("Entities", entities, 0) == ValidationResponse.OK
    assert version_validation("Entities", entities, 1) == ValidationResponse.OK
    assert version_validation("Entities", entities, 2) == ValidationResponse.OK

    assert (
        version_validation("Entities", entities_multi_cnt, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("Entities", entities_multi_cnt, 1)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("Entities", entities_multi_cnt, 2) == ValidationResponse.OK
    )
    with pytest.raises(TypeError):
        entities_multi_cnt.add_scenario_object("tar", veh, [cnt, "dummy"])


def test_external_object():
    ext_obj = OSC.ExternalObjectReference("my object")
    ext_obj2 = OSC.ExternalObjectReference("my object")
    ext_obj3 = OSC.ExternalObjectReference("my object 2")

    assert ext_obj == ext_obj2
    assert ext_obj != ext_obj3

    ext_obj4 = OSC.ExternalObjectReference.parse(ext_obj.get_element())
    assert ext_obj == ext_obj4
    assert (
        version_validation("ExternalObjectReference", ext_obj, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("ExternalObjectReference", ext_obj, 1)
        == ValidationResponse.OK
    )
    assert (
        version_validation("ExternalObjectReference", ext_obj, 2)
        == ValidationResponse.OK
    )
